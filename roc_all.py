from sklearn import svm
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
from matplotlib import pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
import numpy as np
import sklearn.metrics as metrics
import os
import torch
from torch import nn
import math
from scipy.special import softmax

# fig, axes = plt.subplots(1, 1)

data_path = "./data"

files = []
for user in os.listdir(data_path):
    if "DS_Store" in user:
        continue
    print(user)
    for condition in os.listdir(os.path.join(data_path, user)):
        files.append(pd.read_csv(os.path.join(data_path, user, condition)))

df = pd.concat(files)

class_0 = df[df['label'] == 0]
class_1 = df[df['label'] == 1]
class_count_0, class_count_1 = df['label'].value_counts()
class_1_over = class_1.sample(class_count_0, replace=True)

print(class_count_0, class_count_1)

test = pd.concat([class_1_over, class_0], axis=0)

const_emd = math.sqrt(16 * 16 + 12 * 12)

X = test['emd_gaze_aug']
y = test['label']

print(len(X))

min_emd = np.min(X)
max_emd = np.max(X)

print(min_emd, max_emd)

roc_cross_valid = []
for j in range(5):
    highest_roc_auc = 0
    highest_fpr = 0
    highest_tpr = 0
    highest_threshold = 0
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)
    emds = []
    accs = []
    for i in range(100):
        cur_emd = (max_emd - min_emd) * i / 100 + min_emd
        bin_pred_y = []
        pred_y = []
        for x, y_true in zip(X_train, y_train):
            if x < cur_emd:
                bin_pred_y.append(1)
                pred_y.append((cur_emd - x) / (cur_emd - min_emd))
            else:
                bin_pred_y.append(0)
                pred_y.append((cur_emd - x) / (max_emd - cur_emd))
        # pred_y = softmax(pred_y)
        emds.append(cur_emd)
        accs.append(metrics.accuracy_score(y_train, bin_pred_y))
        
        fpr, tpr, threshold = metrics.roc_curve(y_train, pred_y)
        roc_auc = metrics.auc(fpr, tpr)
        if metrics.accuracy_score(y_train, bin_pred_y) > highest_roc_auc:
            highest_roc_auc = metrics.accuracy_score(y_train, bin_pred_y)
            highest_fpr = fpr
            highest_tpr = tpr
            highest_threshold = cur_emd
    print(highest_roc_auc, highest_threshold)
    pred_y = []
    bin_pred_y = []
    for x, y_true in zip(X_test, y_test):
        if x < highest_threshold:
            bin_pred_y.append(1)
            pred_y.append((cur_emd - x) / (cur_emd - min_emd))
        else:
            bin_pred_y.append(1)
            pred_y.append((cur_emd - x) / (max_emd - cur_emd))
    # pred_y = softmax(pred_y)
    print(metrics.accuracy_score(y_test, bin_pred_y))
    fpr, tpr, threshold = metrics.roc_curve(y_test, pred_y)
    roc_auc = metrics.auc(fpr, tpr)
    roc_cross_valid.append(roc_auc)

    # print(highest_threshold)

    plt.plot(highest_fpr, highest_tpr, 'b', label = 'AUC = %0.2f' % highest_roc_auc)
    plt.legend(loc = 'lower right')
    plt.plot([0, 1], [0, 1],'r--')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.ylabel('True Positive Rate')
    plt.xlabel('False Positive Rate')
    plt.show()

    # plt.plot(emds, accs)
    # plt.show()

print(np.mean(np.array(roc_cross_valid)), np.std(np.array(roc_cross_valid)))
