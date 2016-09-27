# -*- coding:utf-8 -*-
from __future__ import division
import numpy as np
import pandas as pd
from extract import *


class Classifier(object):
    """judge auc item interested"""

    def __init__(self, dataPath):
        # load sampleData
        # format is
        # cols: aucitem interested
        self.sampleData = self.loadData(dataPath)
        self.clsValues = self.sampleData[COL_INTERESTED].unique()

    def validate(self, bucketNum=2):
        sd = self.splitData(bucketNum)
        trainData = sd[0]
        testData = sd[1]

        self.train(trainData)
        return self.test(testData)

    def train(self, trainData):
        # group words by cls
        clsWds = {}
        for cls in self.clsValues:
            clsWds[cls] = []
        for idx, row in trainData:
            cls = row[COL_INTERESTED]
            itmWds = self.extractWords(cls)
            clsWds[cls].append(itmWds)

        # calc word prob in every cls
        self.wdProbs = pd.DataFrame(columns=self.clsValues)
        for cls in clsWds:
            for wd in clsWds[cls]:
                if np.isnan(self.wdProbs[cls][wd]):
                    num = 0
                    for w in clsWds[cls]:
                        if w == wd:
                            num += 1
                    self.wdProbs[cls][wd] = num
