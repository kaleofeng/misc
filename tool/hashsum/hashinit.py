#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import json
import os
import random
import time
import shutil
import sys

specificDir= '.mzs'
specificName = 'meta'

def joinPath(basePath, subPath):
    resultPath = os.path.join(basePath, subPath)
    resultPath = resultPath.replace('\\', '/', -1)
    return resultPath

def removeDir(dirPath):
    pathExists = os.path.exists(dirPath)
    if pathExists:
        shutil.rmtree(dirPath)

def makeDir(dirPath):
    os.mkdir(dirPath)

def formatLine(prefix, fileSum, itemPath):
    formatText = '{} {} {}\n'
    itemLine = formatText.format(prefix, fileSum, itemPath)
    return itemLine

def hashFile(filePath):
    with open(filePath, 'rb') as f:
        content = f.read()
        sha256 = hashlib.sha256()
        sha256.update(content)
        result = sha256.hexdigest()
        return result

def hashDir(basePath, relativePath):
    print('-----', basePath, relativePath, '-----')

    dirPath = joinPath(basePath, relativePath)

    baseMetaPath = joinPath(basePath, specificDir)
    dirMetaPath = joinPath(baseMetaPath, relativePath)
    removeDir(dirMetaPath)
    makeDir(dirMetaPath)

    sdPaths = []
    sfPaths = []
    itemLines = []

    for item in os.listdir(dirPath):
        itemPath = joinPath(dirPath, item)

        isDir = os.path.isdir(itemPath)
        if isDir:
            sdPaths.append((item, itemPath))

        isFile = os.path.isfile(itemPath)
        if isFile:
            sfPaths.append((item, itemPath))

    for sdPath in sdPaths:
        sDirName = sdPath[0]
        sDirPath = sdPath[1]
        isSpecific = sDirPath.find(specificDir) >= 0
        if isSpecific:
            continue

        sRelativePath = joinPath(relativePath, sDirName)
        itemSum = hashDir(basePath, sRelativePath)
        itemLine = formatLine('d', itemSum, sDirName)
        itemLines.append(itemLine)

    for sfPath in sfPaths:
        sFileName = sfPath[0]
        sFilePath = sfPath[1]
        itemSum = hashFile(sFilePath)
        itemLine = formatLine('f', itemSum, sFileName)
        itemLines.append(itemLine)

    metaFilePath = joinPath(dirMetaPath, specificName)
    with open(metaFilePath, 'w') as f:
        f.writelines(itemLines)

    for itemLine in itemLines:
        print(itemLine, end='')

    selfSum = hashFile(metaFilePath)
    selfLine = formatLine('s', selfSum, '.')
    print(selfLine, end='')

    print('=====', basePath, relativePath, '=====')
    return selfSum

def hashInit(dirPath):
    hashDir(dirPath, '')

if __name__ == '__main__':
    dirPath = sys.argv[1]
    hashInit(dirPath)
