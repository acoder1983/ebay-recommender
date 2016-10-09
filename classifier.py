# -*- coding:utf-8 -*-
from __future__ import division

import os
import re
import sys
import voc
import numpy as np
import pandas as pd
import unittest as ut

from extract import COL_AUCITEM, COL_INTERESTED, SAMPLE_DATA_COLS, INTERESTED, NOT_INTERESTED, CLS_VALUES
from voc import DATA_DIR


class Classifier(object):
    """judge auc item interested"""

    def __init__(self):
        # load sampleData
        # format is
        # cols: aucitem interested
        self.clsValues = pd.Series(CLS_VALUES)

    def loadData(self, dataPath):
        paths = os.listdir(dataPath)
        df = pd.DataFrame(columns=[COL_AUCITEM, COL_INTERESTED])
        for p in paths:
            if self.isSampleData(p):
                items = pd.read_csv(os.path.join(DATA_DIR, p))
                self.checkClsValues(items.copy(),p)
                df = df.append(items, ignore_index=True)
                print 'load %s' % p
        self.sampleData = df

        return df

    def checkClsValues(self, items,filePath):
        for cls in self.clsValues:
            items = items[items.interested != cls]
        if len(items) > 0:
            print 'error class value in %s' % filePath
            print items
            sys.exit(0)

    def isSampleData(self, filePath):
        pattern = re.compile('\d+\.csv')
        return pattern.match(filePath) != None

    def splitData(self, bucketNum):
        '''
        split dataset into buckets
        :param bucketNum:
        :return: array contains bucketNum df
        '''
        bucketDataSet = []
        for x in xrange(bucketNum):
            d = pd.DataFrame(columns=SAMPLE_DATA_COLS)
            bucketDataSet.append(d)

        clsIdxs = {}
        for i in xrange(self.clsValues.size):
            clsIdxs[self.clsValues[i]] = i
        clsBucIdxs = np.zeros(self.clsValues.size, dtype=np.int16)
        for i, row in self.sampleData.iterrows():
            clsIdx = clsIdxs[row.interested]
            bucIdx = clsBucIdxs[clsIdx]
            bucketDataSet[bucIdx] = bucketDataSet[bucIdx].append(row, ignore_index=True)
            if bucIdx == bucketNum - 1:
                bucIdx = 0
            else:
                bucIdx += 1
            clsBucIdxs[clsIdx] = bucIdx
        return bucketDataSet

    def validate(self, dataPath, bucketNum=2):
        sampleData = self.loadData(dataPath)

        sd = self.splitData(bucketNum)
        trainData = sd[0]
        testData = sd[1]

        self.train(trainData)
        print self.test(testData)

    def train(self, trainData):
        '''
        :param trainData:
        :output:
        1. dict of word prob by class
        key: class value
        value: class df by [word count prob]
        2. dict of class prob
        key: class value
        value: class prob
        3. prob of word not in class
        '''

        # group items by cls
        clsWords = []
        clsItems = []
        for cls in self.clsValues:
            items = trainData[trainData.interested == cls]
            clsWords.append(voc.countWords(items.aucitem))
            clsItems.append(items)

        # calc word prob in every cls
        self.wdProbs = {}
        self.nWdProbs = {}
        self.clsProbs = {}
        for i in xrange(self.clsValues.size):
            cls = self.clsValues[i]
            wdProbs = {}
            vocNum = np.sum(clsWords[i].counts)
            wordNum = clsWords[i].size
            for idx, row in clsWords[i].iterrows():
                wdProbs[row.word] = np.log((row.counts + 1) / (vocNum + wordNum))
            self.wdProbs[cls] = wdProbs
            # calc not in class word prob
            self.nWdProbs[cls] = np.log(1 / (vocNum + wordNum))
            # calc cls prob
            self.clsProbs[cls] = np.log(len(clsItems[i]) / len(trainData))

    def test(self, testData):
        corrects = 0.
        for i, row in testData.iterrows():
            if self.isRight(row):
                corrects += 1

        return corrects * 100 / len(testData)

    def isRight(self, dataRow):
        # extract words of item
        words = voc.extractWords(dataRow.aucitem)

        # calc class prob
        # find the max one
        maxProb = -9e10
        for cls in self.clsValues:
            prob = self.clsProbs[cls]
            for w in words:
                if w in self.wdProbs[cls]:
                    prob += self.wdProbs[cls][w]
                else:
                    prob += self.nWdProbs[cls]
            if prob > maxProb:
                maxProb = prob
                predCls = cls

        # compare with result
        return predCls == dataRow.interested


class TestClassifier(ut.TestCase):
    def testIsSampleData(self):
        c = Classifier()
        self.assertTrue(c.isSampleData('1.csv'))
        self.assertFalse(c.isSampleData('1-2.csv'))
        self.assertTrue(c.isSampleData('12.csv'))

    def testLoadData(self):
        c = Classifier()
        df = c.loadData(DATA_DIR)
        self.assertEqual(df.columns.size, len(SAMPLE_DATA_COLS))
        self.assertTrue(len(df) > 100)
        self.assertTrue(len(df[df.interested == INTERESTED]) > 10)

    def testSplitData(self):
        c = Classifier()

        c.sampleData = pd.read_csv(os.path.join(DATA_DIR, '1.csv'))
        dataSet = c.splitData(2)
        yesData = c.sampleData[c.sampleData.interested == INTERESTED]
        self.assertEqual(len(dataSet[0][dataSet[0].interested == INTERESTED]),
                         len(dataSet[1][dataSet[1].interested == INTERESTED]))

        c.sampleData = pd.read_csv(os.path.join(DATA_DIR, '6.csv'))
        dataSet = c.splitData(2)
        yesData = c.sampleData[c.sampleData.interested == INTERESTED]
        self.assertEqual(1, abs(len(dataSet[0][dataSet[0].interested == INTERESTED]) - len(
            dataSet[1][dataSet[1].interested == INTERESTED])))


if __name__ == '__main__':
    c = Classifier()
    c.validate(DATA_DIR)
