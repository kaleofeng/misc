#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import json
import os
import random
import time
import shutil
import sys

specificDir= ".mzs"
specificName = "meta"

def joinPath(basePath, subPath):
    resultPath = os.path.join(basePath, subPath)
    resultPath = resultPath.replace("\\", "/", -1)
    return resultPath

def makeOrClearDir(dirPath):
    pathExists = os.path.exists(dirPath)
    if pathExists:
        print("remove dir", dirPath)
        shutil.rmtree(dirPath)
    
    print("make dir", dirPath)
    os.mkdir(dirPath)

def hashFile(filePath):
    with open(filePath, 'rb') as f:
        content = f.read()
        sha256 = hashlib.sha256()
        sha256.update(content)
        result = sha256.hexdigest()
        return result

def hashItemLine(prefix, filePath, itemPath):
    fileSum = hashFile(filePath)
    formatText = "{} {} {}"
    itemLine = formatText.format(prefix, fileSum, itemPath)
    return itemLine

def hashDir(dirPath, dirMetaPath):
    print("-----", dirPath, dirMetaPath, "-----")
    
    makeOrClearDir(dirMetaPath)

    metaFilePath = joinPath(dirMetaPath, specificName)
    with open(metaFilePath, 'w') as f:
        sdPaths = []
        sfPaths = []

        for item in os.listdir(dirPath):
            itemPath = joinPath(dirPath, item)
            itemMetaPath = joinPath(dirMetaPath, item)

            isDir = os.path.isdir(itemPath)
            if isDir:
                sdPaths.append((itemPath, itemMetaPath))

            isFile = os.path.isfile(itemPath)
            if isFile:
                sfPaths.append((itemPath, itemMetaPath))

        for sdPath in sdPaths:
            sDirPath = sdPath[0]
            sDirMetaPath = sdPath[1]
            isSpecific = sDirPath.find(specificDir) >= 0
            if isSpecific:
                continue

            hashDir(sDirPath, sDirMetaPath)

            sMetaFilePath = os.path.join(sDirMetaPath, specificName)
            itemLine = hashItemLine("d", sMetaFilePath, sDirPath)
            f.write(itemLine)
            f.write("\n")
            print(itemLine)

        for sfPath in sfPaths:
            sFilePath = sfPath[0]
            itemLine = hashItemLine("f", sFilePath, sFilePath)
            f.write(itemLine)
            f.write("\n")
            print(itemLine)
    
    print("=====", dirPath, dirMetaPath, "=====")

def hashInit(dirPath):
    dirMetaPath = joinPath(dirPath, specificDir)
    hashDir(dirPath, dirMetaPath)

if __name__ == '__main__':
    dirPath = sys.argv[1]
    absPath = os.path.abspath(dirPath)
    hashInit(dirPath)
