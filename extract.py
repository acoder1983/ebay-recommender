# -*- coding:utf-8 -*-
import sys
import numpy as np
import pandas as pd
import unittest as ut
from bs4 import BeautifulSoup

COL_AUCITEM = 'aucitem'
COL_INTERESTED = 'interested'
SAMPLE_DATA_COLS = [COL_AUCITEM, COL_INTERESTED]
INTERESTED = 'yes'
NOT_INTERESTED = 'no'


def extractAutItems(html):
    '''
    extract auc items in html page into
    item sample file in csv format
    @html: html page text
    @return: list of items in dataFrame
    '''
    bs = BeautifulSoup(html, "html5lib")
    df = pd.DataFrame(columns=SAMPLE_DATA_COLS)
    imgs = []
    for img in bs.find_all('img'):
        if img.has_attr('alt') and img.has_attr('class') and img['class'][0] == 'img' and len(img['alt']) > 0:
            imgs.append(img)
            df = df.append(
                {COL_AUCITEM: img['alt'], COL_INTERESTED: NOT_INTERESTED}, ignore_index=True)
    print 'valid imgs', len(imgs)
    return df


class Test(ut.TestCase):

    def testBs(self):
        img = '<img alt="[85904] Ascension good lot Very Fine MNH stamps" class="img" src="http://thumbs.ebaystatic.com/images/g/xKwAAOSwmLlX3oDc/s-l225.jpg"/>'
        bs = BeautifulSoup(img, 'html5lib')
        self.assertTrue(bs.find_all('img')[0].has_attr('class'))
        self.assertEqual('img', bs.find_all('img')[0]['class'][0])
        self.assertEqual('[85904] Ascension good lot Very Fine MNH stamps', bs.find_all(
            'img')[0]['alt'])

    def testExtract(self):
        f = open('data/1.html')
        htmlText = f.read()
        f.close()
        df = extractAutItems(htmlText)
        self.assertEqual(48, len(df))
        self.assertEqual(
            '[85904] Ascension good lot Very Fine MNH stamps', df[COL_AUCITEM][0])
        self.assertEqual('[85950] Hong Kong Birds good complete booklet Very Fine MNH', df[
                         COL_AUCITEM][47])
        self.assertEqual(NOT_INTERESTED, df[
                         COL_INTERESTED][47])


if __name__ == '__main__':
    f = open(sys.args[1])
    htmlText = f.read()
    f.close()
    df = extractAutItems(htmlText)
    # df.to_csv(sys.path.join(getFilePath(f), '.csv')
