#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@File   :   train.py
@Author :   Song
@Time   :   2022/10/25 17:26
@Contact:   songjian@westlake.edu.cn
@intro  :
'''
import copy
import h5py
import numpy as np
import pandas as pd
import torch.optim
import torch.utils.data
from pathlib import Path
import matplotlib.pyplot as plt
import time
from sklearn.metrics import precision_recall_curve, auc

import param_g
from log import Logger
import dataloader
from models import DeepMap
from torch.utils.data.dataset import Dataset
from sklearn.model_selection import train_test_split

try:
    profile
except:
    profile = lambda x: x

logger = Logger.get_logger()


class Map_Dataset(Dataset):
    def __init__(self, maps, valid_ion_nums, labels):
        self.maps = maps
        self.valid_ion_nums = valid_ion_nums
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        # 训练数据的rt维度居中有扰动，im维度也需要平衡
        maps = self.maps[idx]  # [ion_num, 13, 100]
        if idx % 2 == 1:
            maps = np.flip(maps, axis=-1)

        y = self.labels[idx]
        valid_ion_num = self.valid_ion_nums[idx]

        return maps, valid_ion_num, y


# @profile
def train_one_epoch(trainloader, model, optimizer, loss_fn):
    device = param_g.device
    model.train()
    epoch_loss = 0.
    for batch_i, (batch_map, batch_map_len, batch_y) in enumerate(trainloader):
        batch_map = batch_map.float().to(device)
        batch_map_len = batch_map_len.long().to(device)
        batch_y = batch_y.long().to(device)

        # forward
        features, batch_pred = model(batch_map, batch_map_len)

        # loss
        batch_loss = loss_fn(batch_pred, batch_y)
        # back
        optimizer.zero_grad()
        batch_loss.backward()
        # update
        optimizer.step()

        # log
        epoch_loss += batch_loss.item()
        # print
        # if batch_idx % print_batch_nums == 0:
        #     elaps = (time.time() - t0) / (batch_idx + 1)
        #     print('Training epoch: [{}], Batch: [{}/{}], '
        #           'batch time: {:.3f}s, loss: {:.3f}'.format(
        #         epoch, batch_idx, len(trainloader), elaps, batch_loss.item()))

    epoch_loss = epoch_loss / (batch_i + 1)

    return epoch_loss


# @profile
def eval_one_epoch(trainloader, model):
    device = param_g.device
    model.eval()
    prob_v, label_v, shift_v = [], [], []

    for batch_i, (batch_map, batch_map_len, batch_y) in enumerate(trainloader):
        batch_map = batch_map.float().to(device)
        batch_map_len = batch_map_len.long().to(device)
        batch_y = batch_y.long().to(device)

        # forward
        with torch.no_grad():
            features, prob = model(batch_map, batch_map_len)
        prob = torch.softmax(prob.view(-1, 2), 1)
        prob = prob[:, 1].tolist()

        prob_v.extend(prob)
        label_v.extend(batch_y.cpu().tolist())

    probs_all = np.array(prob_v)
    labels_all = np.array(label_v)

    # 基于固定阈值计算总acc
    probs_all[probs_all >= 0.5] = 1
    probs_all[probs_all < 0.5] = 0
    acc = sum(probs_all == labels_all) / len(labels_all)
    return acc

    # 基于auc计算指标
    # precision, recall, thres = precision_recall_curve(label_v, prob_v)
    # area = auc(recall, precision)
    # f1 = 2 * (precision * recall) / (precision + recall + 0.00000001)
    # good_idx = np.argmax(f1)
    # f1 = f1[good_idx]
    # precision = precision[good_idx]
    # recall = recall[good_idx]
    # thres = thres[good_idx]
    # return precision, recall, f1, area, thres


def my_collate(items):
    maps, valid_nums, labels = zip(*items)

    xic = torch.tensor(np.stack(maps))
    xic_num = torch.tensor(np.array(valid_nums))
    label = torch.tensor(np.array(labels))

    assert len(xic) == len(xic_num) == len(label)

    return xic, xic_num, label


def main():
    train_ratios = [0.01, 0.1, 0.4, 0.7, 1.]
    # %% 全局参数
    chunk_num = 25

    batch_size = param_g.batch_size
    epochs = 40
    num_workers = 0 if __debug__ else param_g.num_workers
    device = param_g.device

    folder = Path(r'/home/mantou/data_4d/HeLa_Train/model_big_13_50/hdf')
    Logger.set_logger(folder.parent/'log')

    # 构建eval数据
    maps_v, ion_nums_v, labels_v = [], [], []
    for i, dir_hdf in enumerate(folder.glob('*eval.hdf')):
        logger.info('load eval hdf: {}'.format(dir_hdf.stem))
        with h5py.File(dir_hdf, 'r') as f:
            maps_v.append(f['map'][:])
            ion_nums_v.append(f['ion_num'][:])
            labels_v.append(f['label'][:])
    maps = np.vstack(maps_v)
    ion_nums = np.concatenate(ion_nums_v)
    labels = np.concatenate(labels_v)
    dataset_eval = Map_Dataset(maps, ion_nums, labels)
    loader_eval = torch.utils.data.DataLoader(dataset_eval,
                                              batch_size=batch_size,
                                              num_workers=num_workers,
                                              shuffle=True,
                                              pin_memory=True,
                                              collate_fn=my_collate)
    # model, optimizer and loss
    plot_d = {}
    for train_ratio in train_ratios:
        model = DeepMap(
            map_channels=4*(2 + param_g.fg_num),
            nn_in_features=220
        ).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
        loss_fn = torch.nn.CrossEntropyLoss()
        # 构建train数据并训练
        loss_epoch_v, acc_epoch_v = [], []
        for epoch in range(epochs):
            loss_chunk_v = []
            for chunk_idx in range(1, chunk_num):
                maps_v, ion_nums_v, labels_v = [], [], []
                name_key = '*train_' + str(chunk_idx) + '.hdf'
                for i, dir_hdf in enumerate(folder.glob(name_key)):
                    # logger.info('load train hdf: {}'.format(dir_hdf.stem))
                    with h5py.File(dir_hdf, 'r') as f:
                        maps_v.append(f['map'][:])
                        ion_nums_v.append(f['ion_num'][:])
                        labels_v.append(f['label'][:])
                maps = np.vstack(maps_v)
                ion_nums = np.concatenate(ion_nums_v)
                labels = np.concatenate(labels_v)
                train_idx_all = np.arange(len(labels))
                np.random.seed(123)
                np.random.shuffle(train_idx_all)

                # 取一部分作为train
                train_num = int(train_ratio * len(labels))
                train_idx = train_idx_all[:train_num]
                maps = maps[train_idx]
                ion_nums = ion_nums[train_idx]
                labels = labels[train_idx]
                dataset_train = Map_Dataset(maps, ion_nums, labels)
                loader_train = torch.utils.data.DataLoader(dataset_train,
                                                           batch_size=batch_size,
                                                           num_workers=num_workers,
                                                           shuffle=True,
                                                           pin_memory=True,
                                                           collate_fn=my_collate)
                loss = train_one_epoch(loader_train, model, optimizer, loss_fn)
                loss_chunk_v.append(loss)
                info = 'epoch: {}, chunk_idx: {}, loss: {:3f}'.format(
                    epoch, chunk_idx, loss
                )
                logger.info(info)
            loss_epoch = sum(loss_chunk_v) / len(loss_chunk_v)
            loss_epoch_v.append(loss_epoch)
            # eval
            acc = eval_one_epoch(loader_eval, model)
            acc_epoch_v.append(acc)
            # log
            info = 'epoch: {}, loss: {:.3f}, acc: {:.3f}'.format(
                epoch, loss_epoch, acc)
            logger.info(info)

        plot_d[train_ratio] = (loss_epoch_v, acc_epoch_v)

    # plot
    plt.figure()
    plt.subplot(211)
    for train_ratio in train_ratios:
        plt.plot(plot_d[train_ratio][0], label=train_ratio)
    plt.legend()
    plt.ylabel('loss')
    plt.subplot(212)
    for train_ratio in train_ratios:
        plt.plot(plot_d[train_ratio][1], label=train_ratio)
    plt.legend()
    plt.ylabel('acc')

    plt.tight_layout()
    # plt.show()

    dir_out = folder.parent / 'model' / 'loss_and_acc_v.png'
    plt.savefig(dir_out)

    # save plot_d
    import json
    dir_out = folder.parent / 'model' / 'loss_and_acc_v.json'
    with open(dir_out, 'w') as file:
        json.dump(plot_d, file)


if __name__ == '__main__':
    main()
