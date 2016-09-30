# -*- coding:utf-8 -*-
import os
import sys
import pandas as pd
import unittest as ut

from extract import *

COL_WORD = 'word'
COL_COUNT = 'count'
DATA_DIR = 'data'


def voc(items):
    df = pd.DataFrame(columns=[COL_WORD, COL_COUNT])
    v = {}
    for itm in items:
        words = itm.split(' ')
        for w in words:
            if w.isalpha():
                w = w.lower()
                if w not in v:
                    v[w] = 0
                v[w.lower()] += 1
    for w in v:
        df = df.append(
            {COL_WORD: w, COL_COUNT: v[w]}, ignore_index=True)
    return df


def vocFiles(beg, end):
    for i in xrange(beg, end + 1):
        p = os.path.join(DATA_DIR, str(i) + '.csv')
        df = pd.read_csv(p)
        print 'extract vocabulary from %s' % p
        df = voc(df[COL_AUCITEM])
        p = os.path.join(DATA_DIR, 'voc%d.csv ' % i)
        df.to_csv(p, encoding='utf-8', index=False)
        print 'save voc in %s' % p


class TestVoc(ut.TestCase):
    def testSimple(self):
        items = ['D99294  Space  MNH Rwanda']
        df = voc(items)
        print df
        self.assertEqual(df[COL_WORD].size, 3)
        print type(df[df[COL_WORD] == 'space'][COL_COUNT])
        self.assertEqual(df[df[COL_WORD] == 'space'].iloc[0][COL_COUNT], 1)

    def testMulti(self):
        items = ['T310 2010 UNION DES COMORES SPORT OLYMPIC GAMES 2008 PEKIN WINNERS KB+BL MNH',
                 'T311 2010 UNION DES COMORES CHESS LEGENDS LASKER KRAMNIK KASPAROV KB+BL MNH']
        df = voc(items)
        print df
        self.assertEqual(df[COL_WORD].size, 14)
        self.assertEqual(df[df[COL_WORD] == 'des'].iloc[0][COL_COUNT], 2)
        self.assertEqual(df[df[COL_WORD] == 'pekin'].iloc[0][COL_COUNT], 1)


def composeVocFiles():
    paths=os.listdir(DATA_DIR)
    v={}
    for p in paths:
        if p.startswith('voc'):
            df=pd.read_csv(os.path.join(DATA_DIR,p))
            print 'process %s' % p
            for row in df:
                print row[COL_WORD]
                if row[COL_WORD] not in v:
                    v[row[COL_WORD]]=row[COL_COUNT]
                else:
                    v[row[COL_WORD]]+=row[COL_COUNT]
    df=pd.DataFrame(columns=[COL_WORD, COL_COUNT])
    for w in v:
        df = df.append(
            {COL_WORD: w, COL_COUNT: v[w]}, ignore_index=True)

    p = os.path.join(DATA_DIR, 'allwords.csv ')
    df.to_csv(p, encoding='utf-8', index=False)
    print 'gen %s' % p


if __name__ == '__main__':
    if len(sys.argv) == 3:
        beg = int(sys.argv[1])
        end = int(sys.argv[2])
        vocFiles(beg, end)
    else:
        composeVocFiles()
