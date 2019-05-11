#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 2値分類、他クラス分類に関する結果表示(csv出力もする)

import os
# import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import sqrt
from scipy import stats
from utils import folder_create, clopper_pearson, num_count
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve, auc


class Miss_classify(object):
    def __init__(self, idx, y_pred, y_val, W_val, test_folder, miss_folder):
        self.idx = idx
        self.y_pred = y_pred
        self.y_val = y_val
        self.W_val = W_val
        self.test_folder = test_folder
        self.miss_folder = miss_folder

    # miss_detail・・・
    # missは誤答数, true_listは[0, 1, 0, 0]のように示される正解番号リスト
    # pred_listは[0. 1. 0. 1]のように示されるAI解答番号リスト
    # score_listは[[0.1, 0.9], [0.8, 0.2]]のように示されるAI解答リスト
    def miss_detail(self):
        miss = 0
        pre_list = []
        true_list = []
        folder_list = os.listdir(self.test_folder)
        nb_classes = len(folder_list)
        score_list = [[] for x in range(nb_classes)]
        # preはfileごとの確率の羅列
        # pre_listはすべての問題のAIによる回答
        for i, v in enumerate(self.y_pred):
            pre_ans = v.argmax()
            pre_list.append(pre_ans)
            ans = self.y_val[i].argmax()
            true_list.append(ans)
            for idx in range(nb_classes):
                score_list[idx].append(v[idx])
            if pre_ans != ans:
                miss += 1
        return miss, pre_list, true_list, score_list

    def miss_csv_making(self):
        '''
        全てのファイルをフォルダごとにcsvファイルに書き込む
        '''

        miss, pre_list, true_list, score_list = Miss_classify.miss_detail(self)

        # missフォルダ作成
        folder_create(self.miss_folder)
        folder_list = os.listdir(self.test_folder)
        # nb_classes = len(folder_list)

        # クラス分の[]を用意する。
        file_name_list = []
        for num in range(len(pre_list)):
            # y_val[num]は当該ファイルの正答のベクトル、argmaxで正答番号がわかる
            # W_val[num]は当該ファイルのパス、\\で分割し-1にすることで一番最後のファイル名が分かる
            file_name_list.append(self.W_val[num].split("\\")[-1])

        df = pd.DataFrame()
        df["filename"] = file_name_list
        df["true"] = true_list
        df["predict"] = pre_list

        for i, score in enumerate(score_list):
            df[folder_list[i]] = score
        miss_file = "miss" + "_" + str(self.idx) + "." + "csv"
        miss_fpath = os.path.join(self.miss_folder, miss_file)
        df.to_csv(miss_fpath, index=False, encoding="utf-8")
        return

class Miss_regression(object):
    def __init__(self, idx, y_pred, y_val, W_val, miss_folder):
        self.idx = idx
        self.y_pred = y_pred
        self.y_val = y_val
        self.W_val = W_val
        self.miss_folder = miss_folder

    # miss_detail・・・
    # missは誤答数, true_listは[0, 1, 0, 0]のように示される正解番号リスト
    # pred_listは[0. 1. 0. 1]のように示されるAI解答番号リスト
    # score_listは[[0.1, 0.9], [0.8, 0.2]]のように示されるAI解答リスト
    def miss_csv_making(self):

        # missフォルダ作成
        folder_create(self.miss_folder)

        # クラス分の[]を用意する。
        file_name_list = []
        for W in self.W_val:
            file_name_list.append(W.split("\\")[-1])

        df = pd.DataFrame()
        df["filename"] = file_name_list
        df["true"] = self.y_val
        df["predict"] = self.y_pred

        miss_file = "miss" + "_" + str(self.idx) + "." + "csv"
        miss_fpath = os.path.join(self.miss_folder, miss_file)
        df.to_csv(miss_fpath, index=False, encoding="utf-8")
        return



def cross_making(miss_folder, k, cross_file):
    true_list = []
    predict_list = []
    df_pre_cross = pd.DataFrame(columns=["true", "predict"])
    for i in range(k):
        csv_file = "miss_" + str(i) + ".csv"
        csv_fpath = os.path.join(miss_folder, csv_file)
        df = pd.read_csv(csv_fpath, encoding="utf-8")
        true = df["true"]
        predict = df["predict"]
        true_list.extend(true)
        predict_list.extend(predict)

    df_pre_cross["true"] = true_list
    df_pre_cross["predict"] = predict_list
    df_cross = pd.crosstab(
        df_pre_cross["predict"], df_pre_cross["true"], margins=True)
    df_cross.to_csv(cross_file, encoding="utf-8")
    return


def miss_summarize(miss_folder, miss_file):
    df2 = pd.DataFrame()
    for csv_file in os.listdir(miss_folder):
        csv_fpath = os.path.join(miss_folder, csv_file)
        df = pd.read_csv(csv_fpath, encoding="utf-8")
        df2 = df2.append(df)
    df2.to_csv(miss_file, encoding="utf-8", index=False)
    return

def summary_analysis_binary(miss_summary_file, summary_file, roc_fig, img_folder,alpha):
    df = pd.read_csv(miss_summary_file, encoding="utf-8")
    df0 = df[df["true"] == 0]
    df1 = df[df["true"] == 1]
    n_normal = len(df0)
    n_des = len(df1)
    y_pred = np.array(df[os.listdir(img_folder)[1]])
    y_true = np.array(df["true"])

    # AUCについて
    # y_pred, y_trueを用いて95%信頼区間を求める
    AUCs = roc_auc_ci(y_true, y_pred, alpha, positive = 1)
    print("AUC")
    print(AUCs)

    # 感度1について
    k_des = len(df1[df1["predict"] == 1])
    sensitivity = float(k_des/n_des)
    sensitivity_low, sensitivity_up = clopper_pearson(k_des, n_des, alpha)
    sensitivities = [sensitivity, sensitivity_low, sensitivity_up]
    print("感度")
    print(sensitivities)

    # 特異度1について
    k_normal = len(df0[df0["predict"] == 0])
    specificity = float(k_normal/n_normal)
    specificity_low, specificity_up = clopper_pearson(
        k_normal, n_normal, alpha)
    specificities = [specificity, specificity_low, specificity_up]
    print("特異度")
    print(specificities)


    df_out = pd.DataFrame()
    df_out["AUC"] = AUCs
    df_out["sensitivity"] = sensitivities
    df_out["specificity"] = specificities

    df_out.to_csv(summary_file, index=False, encoding="utf-8")

    fpr, tpr, thresholds = roc_curve(y_true, y_pred)
    roc_auc = auc(fpr, tpr)
    plt.figure()
    plt.plot(fpr, tpr, linewidth=3,
             label='ROC curve (area = %0.3f)' % roc_auc)
    plt.scatter(np.array(1-specificity), np.array(sensitivity), s = 50, c = "green")
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC curve')
    plt.legend(loc="lower right")
    plt.savefig(roc_fig)
    return



def roc_auc_ci(y_true, y_score, alpha, positive=1):
    AUC = roc_auc_score(y_true, y_score)
    # 有病グループの数がN1, 正常群の数がN2
    N1 = sum(y_true == positive)
    N2 = sum(y_true != positive)
    # Q1は
    Q1 = AUC / (2 - AUC)
    Q2 = 2*AUC**2 / (1 + AUC)
    SE_AUC = sqrt((AUC*(1 - AUC) + (N1 - 1)*(Q1 - AUC**2) + (N2 - 1)*(Q2 - AUC**2)) / (N1*N2))
    a,b = stats.norm.interval(alpha, loc=0, scale=1)
    lower = AUC + a*SE_AUC
    upper = AUC + b*SE_AUC
    if lower < 0:
        lower = 0
    if upper > 1:
        upper = 1
    return [AUC,lower, upper]


def summary_analysis_categorical(miss_summary_file, summary_file, img_folder,alpha):
    df = pd.read_csv(miss_summary_file, encoding="utf-8")
    cols = os.listdir(img_folder)
    df_out = pd.DataFrame()
    for i,col in enumerate(cols):
        df0 = df[df["true"] == i]
        n_0 = len(df0)
        df00 = df0[df0["predict"] == i]
        k_0 = len(df00)
        accuracy = float(k_0/n_0)
        accuracy_low, accuracy_up = clopper_pearson(k_0, n_0, alpha)
        accuracies = [accuracy, accuracy_low, accuracy_up]
        print(col)
        print(accuracies)
        df_out[col] = accuracies
    df_out.to_csv(summary_file, index=False, encoding="utf-8")
    return


def summary_analysis_regression(miss_summary_file, summary_file, fig_file):
    df = pd.read_csv(miss_summary_file, encoding="utf-8")
    y_true = df["true"]
    y_pred = df["predict"]
    r, p = stats.pearsonr(y_true, y_pred)
    print("相関係数")
    print(r, p)
    df_out = pd.DataFrame()
    df_out["pearsonr"] = r,p
    df_out.to_csv(summary_file, index=False, encoding="utf-8")

    plt.figure()
    plt.scatter(y_true, y_pred)
    plt.xlabel('Ground value')
    plt.ylabel('Predict Value')
    plt.title('Prediction')
    plt.savefig(fig_file)
