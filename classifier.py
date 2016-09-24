from __future__ import division
import numpy as np
import pandas as pd


class Classifier(object):
    """judge auc item interested"""
    CLS_COL = 'interested'

    def __init__(self, dataPath):
        # load sampleData
        # format is
        # cols: aucitem interested
        self.sampleData = loadData(dataPath)
        self.clsValues = self.sampleData[CLS_COL].unique()

    def validate(self, bucketNum=2):
        sd = splitData(bucketNum)
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
            cls = row[CLS_COL]
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
