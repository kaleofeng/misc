#!/usr/bin/env python
#  -*- coding:utf-8 -*-

import io
import os
import pymysql
import sys
import time
import xlrd

'''
xls文件格式：
第一行：ID  名称    ...
第二行：ID  Name    ...
第三行：int string  ...
第四行：1   苹果    ...
第五行：2   香蕉    ...
...
支持递归遍历
'''

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def readFromXls(xlsUri, records):
    wb = xlrd.open_workbook(xlsUri)
    sheets = wb.sheets()
    sheet = sheets[0]

    nrows = sheet.nrows
    ncols = sheet.ncols

    head = []
    typeRow = sheet.row_values(2)
    for j in range(0, ncols):
        colText = str(typeRow[j])
        head.append(colText)

    for i in range(0, nrows):
        row = sheet.row_values(i)
        rowText = ''
        for j in range(0, ncols):
            col = row[j]
            if i > 2 and head[j] == 'int':
                col = int(col)
            colText = str(col)
            rowText += colText
            if (j < ncols - 1):
                rowText += '\t'
        rowText += '\n'
        records.append(rowText)

    print('Read from file xls[%s] done' %(xlsUri))

def writeIntoTxt(txtUri, records):
    file = open(txtUri, 'w', encoding='utf-8')
    file.writelines(records)
    file.close()
    print('Write into file txt[%s] done' %(txtUri))

rootDir = os.getcwd()
rootDir = './'
xlsDir = ''
txtDir = 'txt/'
print(rootDir, xlsDir, txtDir)

xlsRoot = rootDir + xlsDir
txtRoot = rootDir + txtDir

for parent, dirnames, filenames in os.walk(xlsRoot,  followlinks=True):
    print('1', parent, dirnames, filenames)

    parent = str.replace(parent, '\\', '/')
    if (parent + '/').startswith(txtRoot):
        continue

    print('2', parent, dirnames, filenames)

    rootPos = parent.find(xlsRoot)
    rootLength = len(xlsRoot)
    relativePath = parent[rootLength:]
    print('3', rootPos, rootLength, relativePath)

    xlsPath = parent
    txtPath = '%s%s' %(txtRoot, relativePath)
    print('4', xlsPath, txtPath)

    for filename in filenames:
        pos = filename.find('.xls')
        if pos >= 0:
            if not os.path.exists(txtPath):
                os.makedirs(txtPath)

            filePrefix = filename[0:pos]
            xlsUri = '%s/%s' %(xlsPath, filename)
            txtUri = '%s/%s%s' %(txtPath, filePrefix, '.txt')
            print('9', xlsUri, txtUri)

            records = []
            readFromXls(xlsUri, records)
            writeIntoTxt(txtUri, records)
