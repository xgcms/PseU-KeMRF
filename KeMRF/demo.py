import warnings

warnings.filterwarnings('ignore')
from MultinomialRF import MultinomialRF
import numpy as np
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score, matthews_corrcoef
import pandas as pd


def sen(Y_test, Y_pred):
    con_mat = confusion_matrix(Y_test, Y_pred)
    tp = con_mat[0][0]
    fn = con_mat[0][1]
    sen1 = tp / (tp + fn)
    return sen1


def spe(Y_test, Y_pred):
    con_mat = confusion_matrix(Y_test, Y_pred)
    fp = con_mat[1][0]
    tn = con_mat[1][1]
    spe1 = tn / (tn + fp)
    return spe1


def train_test(train_set, test_set, feature_attr):
    clf = MultinomialRF(n_estimators=100,
                        min_samples_leaf=5,
                        B1=5,
                        B2=5,
                        B3=None,
                        partition_rate=1,
                        n_jobs=1)

    clf.fit(train_set[:, :-1], train_set[:, -1], feature_attr)

    An = []
    for row in test_set[:, :-1]:
        An.append(clf.predict(row))
    An = np.array(An)

    predict_result = []
    for row in train_set[:, :-1]:
        predict_result.append(clf.predict(row))
    predict_result = np.array(predict_result)

    M = []
    for i in range(len(An)):
        K = []
        # 求K
        for xi in predict_result:
            count = 0
            for l in range(len(xi)):
                if tuple(xi[l]) == tuple(An[i][l]):
                    count = count + 1
            Ki = (1 / len(An[0])) * count
            K.append(Ki)
        m1 = 0
        m2 = 0
        for j in range(len(predict_result)):
            m1 = m1 + train_set[j, -1] * K[j]
            m2 = m2 + K[j]
        m = m1 / m2
        M.append(m)

    pre_y = [0 for i in range(len(M))]
    for i in range(len(M)):
        if M[i] < 0:
            pre_y[i] = -1
        elif M[i] > 0:
            pre_y[i] = 1

    return accuracy_score(pre_y, test_set[:, -1].astype(int)), roc_auc_score(pre_y, test_set[:, -1].astype(int)), \
        matthews_corrcoef(pre_y, test_set[:, -1].astype(int)), sen(pre_y, test_set[:, -1].astype(int)), \
        spe(pre_y, test_set[:, -1].astype(int))


def cross_validation(data, feature_attr):
    ACC = []
    AUC = []
    MCC = []
    SN = []
    SP = []
    num = 0

    kf = KFold(n_splits=10, shuffle=True)
    for train_index, test_index in kf.split(X=data[:, :-1], y=data[:, -1], groups=data[:, -1]):
        train_set, test_set = data[train_index], data[test_index]
        acc, auc, mcc, sn, sp = train_test(train_set, test_set, feature_attr)
        ACC.append(acc)
        AUC.append(auc)
        MCC.append(mcc)
        SN.append(sn)
        SP.append(sp)
        print("ROUND[{0}] accuracy score: {1}".format(str(num + 1), str(acc)))
        print("ROUND[{0}] accuracy score: {1}".format(str(num + 1), str(auc)))
        print("ROUND[{0}] accuracy score: {1}".format(str(num + 1), str(mcc)))
        print("ROUND[{0}] accuracy score: {1}".format(str(num + 1), str(sn)))
        print("ROUND[{0}] accuracy score: {1}".format(str(num + 1), str(sp)))
        print("============================================")
        num += 1
    return np.mean(ACC), np.mean(AUC), np.mean(MCC), np.mean(SN), np.mean(SP)


if __name__ == "__main__":

    data = pd.read_csv("./dataset/xxxx.csv")
    for i in range(len(data.iloc[:, 0])):
        if data.iloc[i, 0] == 0:
            data.iloc[i, 0] = -1

    feature = np.array(data.iloc[:, 1:])
    n_features = len(feature[0])
    feature_attr = []
    for i in range(n_features):
        feature_attr.append('c')

    data = np.hstack((feature, np.array(data.iloc[:, 0]).reshape(-1, 1)))
    print(data.shape)

    res, auc, mcc, sn, sp = cross_validation(data, feature_attr)

    print("FINAL accuracy score: {0}".format(str(res)[:6]))
    print("FINAL accuracy score: {0}".format(str(auc)[:6]))
    print("FINAL accuracy score: {0}".format(str(mcc)[:6]))
    print("FINAL accuracy score: {0}".format(str(sn)[:6]))
    print("FINAL accuracy score: {0}".format(str(sp)[:6]))
