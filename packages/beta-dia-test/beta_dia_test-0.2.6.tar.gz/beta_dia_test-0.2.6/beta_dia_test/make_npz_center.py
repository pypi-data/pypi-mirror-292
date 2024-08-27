#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@File   :   make_npz.py
@Author :   Song
@Time   :   2022/11/8 22:13
@Contact:   songjian@westlake.edu.cn
@intro  :   deepmap的负样本需要好好设计，不然模型在训练阶段能有很高acc，但是
            使用阶段的过滤不强。使用正样本其他共流出强的打分来设计负样本。
            rt无需添加扰动，im由于本就是预测值而不是准确测量值，可以不用添加扰动
            从而确保deepmap找到最准确的locus
'''
import warnings
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import torch
from numba import NumbaPerformanceWarning

import deepmap
import fxic
import param_g
from library import Library
from log import Logger
from tims import Tims
from utils import release_gpu_scans

warnings.filterwarnings("ignore", category=NumbaPerformanceWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

try:
    profile
except:
    profile = lambda x: x

logger = Logger.get_logger()

def push_all_zeros_back(a):
    # Based on http://stackoverflow.com/a/42859463/3293881
    valid_mask = a != 0
    flipped_mask = valid_mask.sum(1, keepdims=1) > np.arange(a.shape[1] - 1, -1,
                                                             -1)
    flipped_mask = flipped_mask[:, ::-1]
    a[flipped_mask] = a[valid_mask]
    a[~flipped_mask] = 0
    return a


def split_hdf(maps, ion_nums, labels, chunk_num, dir_out):
    idx_total = np.arange(len(labels))
    np.random.shuffle(idx_total)
    idx_total = np.array_split(idx_total, chunk_num)

    for chunk_idx in range(chunk_num):
        idx = idx_total[chunk_idx]

        maps_chunk = maps[idx]
        ions_num_chunk = ion_nums[idx]
        labels_chunk = labels[idx]

        fname = dir_out.stem
        folder_out = dir_out.parent
        if chunk_idx == 0:
            fout = folder_out / (fname + '_eval.hdf')
        else:
            fout = folder_out / (fname + '_train_' + str(chunk_idx) + '.hdf')

        with h5py.File(fout, 'w') as f:
            f.create_dataset('map', data=maps_chunk)
            f.create_dataset('label', data=labels_chunk)
            f.create_dataset('ion_num', data=ions_num_chunk)


# @profile
def main():
    # 参数
    chunk = 10
    dir_raw = Path(r'/home/mantou/data_4d/HeLa_Train/raw_data')
    dir_ws = Path(r'/home/mantou/data_4d/HeLa_Train/model_center_13_50')
    dir_lib = '/home/mantou/diann_lib_19/human_20420.predicted.speclib'

    # log
    Logger.set_logger(dir_ws / 'log')

    # 读取lib
    lib = Library(dir_lib, worker_num=1 if __debug__ else 8)
    logger.info('load lib finished.')

    for i_ws, ws in enumerate(dir_raw.glob('*.d')):
        # if i_ws > 0:
        #     break

        logger.info(ws)
        logger.info('load ms...')
        ms = Tims(ws)
        logger.info('load ms finished.')

        # 基于ms修正库
        df_target = lib.polish_lib(ms.get_swath(), ws_diann=ws)
        df_target['pred_im'] = df_target['diann_im']

        # 构建map时，rt轴应该是以cycle为单位，预定义cycle_num
        map_cycle_dim = param_g.map_cycle_dim
        map_im_dim = param_g.map_im_dim  # 100 or 50
        im_gap = param_g.map_im_gap
        print(
            f'cycle_num: {map_cycle_dim}, '
            f'im_gap: {im_gap:.5f}, '
            f'map_im_dim: {map_im_dim}'
        )

        # 根据12个子离子确定每个肽段的竞争窗口
        df_target['pred_rt'] = df_target['diann_rt']
        locus_v = []
        measure_ims_v = []
        df_v = []
        for swath_id in df_target['swath_id'].unique():
            df_swath = df_target[df_target['swath_id'] == swath_id]
            df_swath = df_swath.reset_index(drop=True)
            info = 'swath: {}, # target: {}'.format(swath_id, len(df_swath))
            logger.info(info)

            # 当前map_gpu
            map_gpu_ms1c, map_gpu_ms2c = ms.copy_map_to_gpu(swath_id=swath_id,
                                                            centroid=True)
            all_rts = ms.get_scan_rts()
            bias_rts = np.abs(df_swath['diann_rt'].values[:, None] - all_rts)
            locus_diann = np.argmin(bias_rts, axis=1)
            df_swath['locus_diann'] = locus_diann

            # 定位：locus_diann, locus_apex
            N = 10000
            for batch_idx, df_batch in df_swath.groupby(df_swath.index // N):
                df_batch = df_batch.reset_index(drop=True)
                # [k, ions_num, n]，全域提取
                locus, rts, ims, mzs, xics = fxic.extract_xics(
                    df_batch,
                    map_gpu_ms1c,
                    map_gpu_ms2c,
                    param_g.tol_ppm,
                    param_g.tol_im_xic,
                )
                xics = fxic.gpu_simple_smooth(xics)
                scores_sa, scores_sa_m = fxic.cal_coelution_by_gaussion(
                    xics, param_g.window_points, df_batch.fg_num.values + 2
                )
                scores_sa_gpu = fxic.reserve_sa_maximum(scores_sa)

                # 与locus_diann最接近的非零sa值的索引为locus_apex
                scores_sa = scores_sa_gpu.cpu().numpy()
                scores_sa_b = (scores_sa > 0).astype(int)
                locus_diann = df_batch['locus_diann'].values
                tmp = np.abs(locus_diann.reshape(-1, 1) - locus) + 0.1
                tmp = tmp * scores_sa_b
                tmp[tmp <= 0.] = locus.max() * 2
                locus_apex = np.argmin(tmp, axis=1)
                df_batch['locus_apex'] = locus_apex
                df_v.append(df_batch)

                _, idx = torch.topk(scores_sa_gpu,
                                    k=30,
                                    dim=1,
                                    sorted=True)
                locus = locus[np.arange(len(locus))[:, None], idx.cpu()]
                locus_v.append(locus)

                # cal measure_im for maps by locus
                n_pep, n_ion, n_cycle = ims.shape
                ims = ims.transpose(0, 2, 1).reshape(-1, n_ion)
                scores_sa_m = scores_sa_m.transpose(0, 2, 1).reshape(-1, n_ion)
                measure_ims = fxic.cal_measure_im(ims, scores_sa_m)
                measure_ims = measure_ims.reshape(-1, n_cycle)
                measure_ims_v.append(measure_ims)
        locus_neg_m = np.vstack(locus_v)
        measure_ims = np.vstack(measure_ims_v)
        df_target = pd.concat(df_v, ignore_index=True)

        # 查看我们确定的locus和im与DIA-NN确定的locus、im的偏差
        bias = df_target['locus_apex'].values - df_target['locus_diann'].values
        assert (np.abs(bias) > 4).sum() / len(bias) < 0.01

        # 正样本，左右偏1个locus
        locus_pos = df_target['locus_apex'].values
        df_target['decoy'] = 0
        df_target['locus'] = df_target['locus_apex']
        idx_x = np.arange(len(df_target))
        df_target['measure_im'] = measure_ims[idx_x, locus_pos]
        df_target_left = df_target.copy()
        df_target_left['locus'] = df_target_left['locus'] - 1
        df_target_right = df_target.copy()
        df_target_right['locus'] = df_target_right['locus'] + 1
        df_targets = pd.concat([df_target, df_target_left, df_target_right])
        df_targets = df_targets.reset_index(drop=True)
        data_augment_num = int(len(df_targets) / len(df_target))

        # 从df_locus中排除locus_pos，要相距大于7个cycle
        for i in range(locus_neg_m.shape[1]):
            locus = locus_neg_m[:, i]
            good_idx = np.abs(locus - locus_pos) > 7
            locus_neg_m[:, i][~good_idx] = 0
        locus_neg_m = push_all_zeros_back(locus_neg_m)
        locus_neg_m = locus_neg_m[:, :data_augment_num]
        assert (locus_neg_m >= 0).all()

        # 把正、负locus附加到df
        df_v = []
        for i in range(locus_neg_m.shape[1]):
            df = df_target.copy()
            df['locus'] = locus_neg_m[:, i]
            df['measure_im'] = measure_ims[idx_x, locus_neg_m[:, i]]
            df['decoy'] = 1
            df_v.append(df)
        df_negs = pd.concat(df_v, axis=0, ignore_index=True)
        df = pd.concat([df_targets, df_negs], axis=0, ignore_index=True)
        assert df['measure_im'].min() > 0.5
        assert df['measure_im'].max() < 2.

        # 提取map
        cycle_total = len(map_gpu_ms1c['scan_rts'])
        cycle_num = param_g.map_cycle_dim
        locus_m = df['locus'].values.reshape(-1, 1)
        idx_start_bank = locus_m - int((cycle_num - 1) / 2)
        idx_start_bank[idx_start_bank < 0] = 0
        idx_start_max = cycle_total - cycle_num
        idx_start_bank[idx_start_bank > idx_start_max] = idx_start_max

        maps_v, ion_nums_v, labels_v = [], [], []
        for swath_id in df['swath_id'].unique():
            map_gpu_ms1p, map_gpu_ms2p = ms.copy_map_to_gpu(swath_id=swath_id,
                                                            centroid=False)

            df_swath = df[df['swath_id'] == swath_id]
            idx_start_m = idx_start_bank[df_swath.index]
            df_swath = df_swath.reset_index(drop=True)

            for _, df_batch in df_swath.groupby(df_swath.index // 1000):
                ion_nums = 2 + df_batch['fg_num'].values
                ion_nums_v.append(ion_nums)
                labels_v.append(1 - df_batch['decoy'].values)
                maps = deepmap.extract_maps(df_batch,
                                            idx_start_m,
                                            locus_m.shape[1],
                                            cycle_num,
                                            map_im_dim,
                                            map_gpu_ms1p,
                                            map_gpu_ms2p,
                                            param_g.tol_ppm,
                                            param_g.tol_im_map,
                                            param_g.map_im_gap,
                                            neutron_num=0)  # center
                maps = maps.squeeze(dim=1).cpu().numpy()
                maps_v.append(maps)
        release_gpu_scans(map_gpu_ms1p)
        release_gpu_scans(map_gpu_ms2p)

        maps_v = np.vstack(maps_v)
        ion_nums = np.concatenate(ion_nums_v, dtype=np.int8)
        labels = np.concatenate(labels_v)

        fname = ws.name + '.hdf'
        dir_out = dir_ws / 'hdf' / fname
        split_hdf(maps_v, ion_nums, labels, chunk, dir_out)


if __name__ == '__main__':
    main()
