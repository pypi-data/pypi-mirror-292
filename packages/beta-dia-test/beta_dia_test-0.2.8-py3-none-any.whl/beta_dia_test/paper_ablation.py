#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@File   :   nn.py
@Author :   Song
@Time   :   2023/4/17 14:17
@Contact:   songjian@westlake.edu.cn
@intro  :   复现DIA-NN的集成神经网络用于归并子打分
'''
import warnings

import numpy as np
import pandas as pd
import torch.nn as nn
import torch.nn.functional
import torch.utils.data
from sklearn import preprocessing
from sklearn.ensemble import VotingClassifier
from sklearn.exceptions import ConvergenceWarning

warnings.filterwarnings(action='ignore', category=ConvergenceWarning)
warnings.simplefilter("ignore")

import os

os.environ["PYTHONWARNINGS"] = "ignore"  # multiprocess

import param_g
from log import Logger

import utils

try:
    profile
except NameError:
    profile = lambda x: x

logger = Logger.get_logger()


def init_weights(m):
    if type(m) == nn.Linear:
        nn.init.xavier_uniform_(m.weight)


class Model_Classifier(nn.Module):
    def __init__(self, var_num):
        super(Model_Classifier, self).__init__()

        self.layers = nn.ModuleList()

        for i in range(5):
            dim_out = (5 - i) * 5
            if i == 0:
                dim_in = var_num
            else:
                dim_in = dim_out + 5
            self.layers.append(nn.Linear(dim_in, dim_out))

        self.fc = nn.Linear(5, 2)
        self.dropout = nn.Dropout(0.2)

    def forward(self, batch_x):
        for i in range(len(self.layers)):
            batch_x = self.layers[i](batch_x)
            # batch_x = self.dropout(batch_x)
            batch_x = torch.relu(batch_x)
        y = self.fc(batch_x)

        return y


# @profile
def cal_qvalue_second(df_input, batch_size, n_model, top_pep):
    col_idx = df_input.columns.str.startswith('score_')
    logger.info('cols num: {}'.format(sum(col_idx)))

    X = df_input.loc[:, col_idx].to_numpy()
    assert X.dtype == np.float32
    y = 1 - df_input['decoy'].to_numpy()  # 正类是target
    X = preprocessing.scale(X)  # 树模型不用scale

    # 基于group_rank == 1进行训练，再作用到整体
    train_idx = df_input.group_rank == 1
    X_train = X[train_idx]
    y_train = y[train_idx]
    n_pos, n_neg = sum(y_train == 1), sum(y_train == 0)
    info = 'Training the model: {} pos, {} neg'.format(n_pos, n_neg)
    logger.info(info)

    # models
    param = (25, 20, 15, 10, 5)
    mlps = [MLPClassifier(max_iter=1,
                          shuffle=True,
                          random_state=i,  # 用于初始化权重与shuffle的采样
                          learning_rate_init=0.003,
                          solver='adam',
                          batch_size=batch_size,  # 50
                          activation='relu',
                          hidden_layer_sizes=param) for i in range(n_model)]
    names = [f'mlp{i}' for i in range(n_model)]
    model = VotingClassifier(estimators=list(zip(names, mlps)),
                             voting='soft',
                             n_jobs=1 if __debug__ else 12)
    model.fit(X_train, y_train)
    cscore = model.predict_proba(X)[:, 1]

    df_input['cscore_pr'] = cscore

    if df_input['group_rank'].max() > 1:
        group_size = df_input.groupby('pr_id', sort=False).size()
        group_size_cumsum = np.concatenate([[0], np.cumsum(group_size)])
        idx, group_rank = utils.cal_group_rank(df_input.cscore_pr.values,
                                               group_size_cumsum)
        df_input = df_input.loc[idx].reset_index(drop=True)
        df_input['group_rank'] = group_rank

    df_top = df_input[df_input['group_rank'] == 1].reset_index(drop=True)
    df_top = utils.cal_q_pr(df_top, score_col='cscore_pr')

    df_top['strip_seq'] = df_top['simple_seq'].str.upper()
    df_fdr = utils.cal_q_pro(df_top, top_pep=top_pep)
    df_fdr = utils.cal_q_pg(df_fdr, top_pep=top_pep)

    df_result = df_fdr[(df_fdr['decoy'] == 0) &
                       (df_fdr['group_rank'] == 1)].reset_index(drop=True)

    for q in [0.001, 0.01, 0.02, 0.03, 0.05]:
        num_pr = df_result[df_result['q_pr'] <= q]['pr_id'].nunique()
        num_pro = df_result[df_result['q_pro'] <= q]['protein_id'].nunique()
        num_pg = df_result[df_result['q_pg'] <= q]['protein_group'].nunique()

        logger.info(f'Fdr-{q}: #pr-{num_pr}, #pro-{num_pro}, #pg-{num_pg}')

        utils.cal_acc_recall(param_g.ws, df_result,
                             diann_q_pr=q, diann_q_pro=q, diann_q_pg=q,
                             alpha_q_pr=q, alpha_q_pro=q, alpha_q_pg=q)

    return df_result


# Creating a custom MLPDropout classifier
from sklearn.neural_network import MLPClassifier


@profile
def cal_qvalue_first(df_input, batch_size, n_model, q_cut, model_trained=None):
    # df = check_scores_by_priori(df_input)
    df = df_input.copy()

    col_idx = df.columns.str.startswith('score_')
    logger.info('cols num: {}'.format(sum(col_idx)))

    X = df.loc[:, col_idx].to_numpy()
    assert X.dtype == np.float32
    y = 1 - df['decoy'].to_numpy()  # 正类是target
    X = preprocessing.scale(X)  # 树模型不用scale

    # 基于group_rank == 1进行训练，再作用到整体
    train_idx = df.group_rank == 1
    X_train = X[train_idx]
    y_train = y[train_idx]
    n_pos, n_neg = sum(y_train == 1), sum(y_train == 0)
    info = 'Training the model: {} pos, {} neg'.format(n_pos, n_neg)
    logger.info(info)

    # models
    if model_trained is None:
        param = (25, 20, 15, 10, 5)
        mlps = [MLPClassifier(max_iter=1,
                              shuffle=True,
                              random_state=i,  # 用于初始化权重与shuffle的采样
                              learning_rate_init=0.003,
                              solver='adam',
                              batch_size=batch_size,  # 50
                              activation='relu',
                              hidden_layer_sizes=param) for i in range(n_model)]
        names = [f'mlp{i}' for i in range(n_model)]
        model = VotingClassifier(estimators=list(zip(names, mlps)),
                                 voting='soft',
                                 n_jobs=1 if __debug__ else 12)
        model.fit(X_train, y_train)
        cscore = model.predict_proba(X)[:, 1]
    else:
        model = model_trained
        cscore = model.predict_proba(X)[:, 1]

    df['cscore_pr'] = cscore

    if df.group_rank.max() > 1:
        group_size = df.groupby('pr_id', sort=False).size()
        group_size_cumsum = np.concatenate([[0], np.cumsum(group_size)])
        idx, group_rank = utils.cal_group_rank(df.cscore_pr.values,
                                               group_size_cumsum)
        df = df.loc[idx].reset_index(drop=True)
        df['group_rank'] = group_rank

    df_top = df[df['group_rank'] == 1].reset_index(drop=True)
    df_top = utils.cal_q_pr(df_top, score_col='cscore_pr')

    for q_pr in [0.01, q_cut]:
        df_sub = df_top[(df_top['q_pr'] <= q_pr)]
        df_sub = df_sub[df_sub.decoy == 0]
        info = 'Fast fdr: {:.4f}, prs: {}'.format(q_pr, df_sub.pr_id.nunique())
        logger.info(info)
        utils.cal_acc_recall(param_g.ws, df_sub, diann_q_pr=0.01)

    df_cut = df_top[df_top.q_pr < q_cut].reset_index(drop=True)

    return df_cut, model


# @profile
def cal_qvalue_fast_torch(df_input, base_num, num_workers, q_cut):
    df = df_input.copy()

    col_idx = df.columns.str.startswith('score_')
    logger.info('cols num: {}'.format(sum(col_idx)))

    X = df.loc[:, col_idx].to_numpy()
    assert X.dtype == np.float32
    y = 1 - df['decoy'].to_numpy()  # 正类是target
    X = preprocessing.scale(X)  # 树模型不用scale

    # 基于group_rank == 1进行训练，再作用到整体
    train_idx = df.group_rank == 1
    X_train = X[train_idx]
    y_train = y[train_idx]
    n_pos, n_neg = sum(y_train == 1), sum(y_train == 0)
    info = 'Training the model: {} pos, {} neg'.format(n_pos, n_neg)
    logger.info(info)

    # data and model
    X_train, y_train = torch.from_numpy(X_train), torch.from_numpy(y_train)
    X_test = torch.from_numpy(X)
    train_dataset = torch.utils.data.TensorDataset(X_train, y_train)
    test_dataset = torch.utils.data.TensorDataset(X_test)
    torch.manual_seed(0)
    train_loader = torch.utils.data.DataLoader(train_dataset,
                                               batch_size=50,
                                               num_workers=num_workers,
                                               shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_dataset,
                                              batch_size=5012,
                                              num_workers=num_workers,
                                              shuffle=False)
    mlps = [Model_Classifier(X_train.shape[1]).to(param_g.device) for _
            in range(base_num)]
    for mlp in mlps:
        mlp.apply(init_weights)
    optimizer = torch.optim.Adam([{"params": mlp.parameters()} for mlp in mlps],
                                 lr=0.003)
    loss_fn = torch.nn.CrossEntropyLoss()

    # train
    for epoch_i in range(1):
        for batch_idx, (batch_x, batch_y) in enumerate(train_loader):
            batch_x = batch_x.float().to(param_g.device)
            batch_y = batch_y.long().to(param_g.device)
            optimizer.zero_grad()
            for mlp in mlps:
                prob = mlp(batch_x)
                batch_loss = loss_fn(prob, batch_y)
                batch_loss.backward()
            optimizer.step()
    logger.info('Model training finished.')

    # test
    prob_v = [[] for _ in range(base_num)]
    for batch_idx, batch_x in enumerate(test_loader):
        batch_x = batch_x[0].float().to(param_g.device)
        for idx, mlp in enumerate(mlps):
            mlp.eval()
            with torch.no_grad():
                prob = mlp(batch_x)
                prob = torch.softmax(prob.view(-1, 2), 1)
                prob = prob[:, 1].tolist()
                prob_v[idx].extend(prob)

    cscore = np.array(prob_v).mean(axis=0)
    df['cscore_pr'] = cscore

    if df.group_rank.max() > 1:
        group_size = df.groupby('pr_id', sort=False).size()
        group_size_cumsum = np.concatenate([[0], np.cumsum(group_size)])
        idx, group_rank = utils.cal_group_rank(df.cscore_pr.values,
                                               group_size_cumsum)
        df = df.loc[idx].reset_index(drop=True)
        df['group_rank'] = group_rank

    df_top = df[df['group_rank'] == 1].reset_index(drop=True)
    df_top = utils.cal_q_pr(df_top, score_col='cscore_pr')

    for q_pr in [0.01, 0.7]:  # [0.005, 0.01, 0.05, 0.5, 0.7]:
        df_sub = df_top[(df_top['q_pr'] <= q_pr)]
        df_sub = df_sub[df_sub.decoy == 0]
        info = 'Fast fdr: {:.4f}, prs: {}'.format(q_pr, df_sub.pr_id.nunique())
        logger.info(info)
        utils.cal_acc_recall(param_g.ws, df_sub, diann_q_pr=0.01)

    df_cut = df_top[df_top.q_pr < q_cut].reset_index(drop=True)

    return df_cut


if __name__ == '__main__':
    from pathlib import Path

    # ws = Path(r'/SSD-4T/mantou/data_4d/base_test/HeLa_Evosep/60SPD
    # /20200428_Evosep_60SPD_SG06-16_MLHeLa_200ng_py8_S3-A6_1_2452.d')
    ws = Path(
        r'/SSD-4T/mantou/data_4d/base_test/HeLa_Evosep/200SPD'
        r'/20200505_Evosep_200SPD_SG06-16_MLHeLa_200ng_py8_S3-A4_1_2740.d')
    # ws = Path('/SSD-4T/mantou/data_4d/timsUltra_singlecell/20230821_Evo2_IO5_80SPD_scLF_Ola_20230818_DMSO_S2-H4_1_2263.d')

    param_g.ws = Path(ws)
    param_g.dir_out = Path(ws) / 'beta_dia'
    Logger.set_logger(param_g.dir_out)

    df = pd.read_pickle(Path(ws) / 'beta_dia' / 'df_scores2.pkl')

    # 区分cols
    cols = set(df.columns)
    cols_score = set(df.columns[df.columns.str.startswith('score_')])
    cols_nonscore = cols - cols_score

    cols_mall = set(['score_mall']) | set(
        ['score_ft_mall_' + str(i) for i in range(32)])

    cols_center = set(['score_left_deep_pre', 'score_center_deep_pre',
                       'score_1H_deep_pre', 'score_2H_deep_pre',
                       'score_left_deep_refine', 'score_center_deep_refine',
                       'score_1H_deep_refine', 'score_2H_deep_refine',
                       'score_center_deep_pre_putative1',
                       'score_center_deep_pre_putative2',
                       'score_deep_center_sub_left', 'score_coelution_x_center',
                       'score_deep_center_sub_left_refine',
                       'score_coelution_x_center_refine',
                       'score_left_deep_refine_p1',
                       'score_center_deep_refine_p1',
                       'score_1H_deep_refine_p1', 'score_2H_deep_refine_p1',
                       'score_left_deep_refine_p2',
                       'score_center_deep_refine_p2',
                       'score_1H_deep_refine_p2', 'score_2H_deep_refine_p2',
                       ])
    cols_center = cols_center | set(
        ['score_ft_deep_pre_' + str(i) for i in range(128)])
    cols_center = cols_center | set(
        ['score_ft_deep_refine_p1_' + str(i) for i in range(128)])
    cols_center = cols_center | set(
        ['score_ft_deep_refine_p2_' + str(i) for i in range(128)])

    cols_big = set(['score_big_deep_pre', 'score_big_deep_refine',
                    'score_big_deep_pre_putative1',
                    'score_big_deep_pre_putative2',
                    'score_coelution_x_big',
                    'score_coelution_x_big_refine',
                    'score_big_deep_refine_p1',
                    'score_big_deep_refine_p2',
                    ])
    cols_big = cols_big | set(
        ['score_ft_deep_pre_' + str(i) for i in range(128, 160)])
    cols_big = cols_big | set(
        ['score_ft_deep_refine_p1_' + str(i) for i in range(128, 160)])
    cols_big = cols_big | set(
        ['score_ft_deep_refine_p2_' + str(i) for i in range(128, 160)])

    cols_deep = cols_mall | cols_center | cols_big
    cols_func = cols_score - cols_deep
    cols_rt = set(
        ['score_measure_rt', 'score_pred_rt', 'score_rt_abs', 'score_rt_power',
         'score_rt_root', 'score_rt_log', 'score_rt_ratio']
        )
    cols_refine = set(['score_left_deep_refine', 'score_center_deep_refine',
                           'score_1H_deep_refine', 'score_2H_deep_refine',
                           'score_deep_center_sub_left_refine',
                           'score_coelution_x_center_refine',
                           'score_big_deep_refine',
                           'score_coelution_x_big_refine',
                           ])
    result = {}

    # 啥都不去掉
    print('763:')
    dfx, _ = cal_qvalue_first(df, 50, 12, q_cut=1)
    print('\n')
    result['All scores'] = sum((dfx['q_pr'] < 0.01) & (dfx['decoy'] == 0))

    # 去掉refine
    dfx = df.drop(columns=cols_refine)
    print('Remove Refine:')
    dfx, _ = cal_qvalue_first(dfx, 50, 12, q_cut=1)
    print('\n')
    result['Remove Refine'] = sum((dfx['q_pr'] < 0.01) & (dfx['decoy'] == 0))

    # 去掉deepmall
    dfx = df.drop(columns=cols_mall)
    print('Remove DeepMall:')
    dfx, _ = cal_qvalue_first(dfx, 50, 12, q_cut=1)
    print('\n')
    result['Remove DeepMall'] = sum((dfx['q_pr'] < 0.01) & (dfx['decoy'] == 0))

    # 去掉deepcenter
    dfx = df.drop(columns=cols_center)
    print('Remove DeepCenter:')
    dfx, _ = cal_qvalue_first(dfx, 50, 12, q_cut=1)
    print('\n')
    result['Remove DeepProfile-14'] = sum((dfx['q_pr'] < 0.01) & (dfx['decoy'] == 0))

    # 去掉deepbig
    dfx = df.drop(columns=cols_big)
    print('Remove DeepBig:')
    dfx, _ = cal_qvalue_first(dfx, 50, 12, q_cut=1)
    print('\n')
    result['Remove DeepProfile-56'] = sum((dfx['q_pr'] < 0.01) & (dfx['decoy'] == 0))

    # 去掉所有function-based, exclude RT scores
    dfx = df.loc[:, df.columns.isin(cols_nonscore | cols_deep | cols_rt)]
    print('Only deep-based + RT:')
    dfx, _ = cal_qvalue_first(dfx, 50, 12, q_cut=1)
    print('\n')
    result['Only deep-based + RT'] = sum((dfx['q_pr'] < 0.01) & (dfx['decoy'] == 0))

    # 去掉所有deep，只考虑函数式打分
    dfx = df.drop(columns=cols_deep)
    print('Only function-based:')
    dfx, _ = cal_qvalue_first(dfx, 50, 12, q_cut=1)
    print('\n')
    result['Only function-based'] = sum((dfx['q_pr'] < 0.01) & (dfx['decoy'] == 0))

    # plot
    import matplotlib.pyplot as plt

    bars = plt.bar(list(result.keys()), list(result.values()), color='skyblue')
    plt.xticks(rotation=45)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 4, yval, int(yval),
                 va='bottom')  # va='bottom'将文本放在条形的顶部

    plt.tight_layout()
    plt.show()
