#!/usr/bin/env python
# -*- coding: utf-8 -*-

import exifread
import hashlib
import json
import os
import random
import re
import shutil
import sys
import time

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

def visitDir(basePath, relativePath, extensions, visitFile):
    print('-----', basePath, relativePath, extensions, '-----', flush=True)

    dirPath = joinPath(basePath, relativePath)

    baseMetaPath = joinPath(basePath, specificDir)
    dirMetaPath = joinPath(baseMetaPath, relativePath)
    removeDir(dirMetaPath)
    makeDir(dirMetaPath)

    sdPaths = []
    sfPaths = []
    fileTagMap = {}

    for entryName in os.listdir(dirPath):
        result = re.search(r'({})$'.format(extensions), entryName)
        if result == None:
          continue

        entryPath = joinPath(dirPath, entryName)

        isDir = os.path.isdir(entryPath)
        if isDir:
            sdPaths.append((entryName, entryPath))

        isFile = os.path.isfile(entryPath)
        if isFile:
            sfPaths.append((entryName, entryPath))

    for sdPath in sdPaths:
        sDirName = sdPath[0]
        sDirPath = sdPath[1]
        isSpecific = sDirPath.find(specificDir) >= 0
        if isSpecific:
            continue

        sRelativePath = joinPath(relativePath, sDirName)
        visitDir(basePath, sRelativePath, extensions, visitFile)

    for sfPath in sfPaths:
        sFileName = sfPath[0]
        sFilePath = sfPath[1]
        fileTag = visitFile(sFilePath)
        filePathList = fileTagMap.setdefault(fileTag, [])
        filePathList.append(sFilePath)

    for (fileTag, filePathList) in fileTagMap.items():
      print(fileTag, len(filePathList), flush=True)

      tagMetaPath = joinPath(dirMetaPath, fileTag)
      print(tagMetaPath, flush=True)
      makeDir(tagMetaPath)

      for filePath in filePathList:
        print('copy {} to {}'.format(filePath, tagMetaPath), flush=True)
        shutil.copy(filePath, tagMetaPath)

      print('', flush=True)

def visitInit(dirPath, extensions, visitFile):
    print('visit Init: ', dirPath, extensions, flush=True)

    visitDir(dirPath, '', extensions, visitFile)

def classifyFileByDate(filePath):
    with open(filePath, 'rb') as f:
        tags = exifread.process_file(f)
        print(tags)
        imageDateTime = tags.get('Image DateTime', '0')
        if (imageDateTime != '0'):
          imageDateTime = imageDateTime.values
        imageDate = re.sub(r'^(\d{4}):(\d{2}):(\d{2})(.*)$', r'\g<1>-\g<2>-\g<3>', imageDateTime)
        return imageDate

if __name__ == '__main__':
    dirPath = sys.argv[1]
    extensions = sys.argv[2]
    mode = sys.argv[3]

    if mode == 'date':
      visitInit(dirPath, extensions, classifyFileByDate)
