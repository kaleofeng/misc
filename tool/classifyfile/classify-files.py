#!/usr/bin/env python
# -*- coding: utf-8 -*-

import calendar
import glob
import exifread
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time

from pymediainfo import MediaInfo

specificDir= '.mzs'
specificName = 'meta'

extensions = '' # Filter file extensions(for example: 'jpg|mp4|mov'), '' for all extensions
mode = '0'      # Whether put all date dirs to root directory [0] No [1] yes

processedCount = 0
unprocessedFiles = set()
exceptionalFiles = set()

def joinPath(basePath, subPath):
  resultPath = os.path.join(basePath, subPath)
  resultPath = resultPath.replace('\\', '/', -1)
  return resultPath

def normalizePath(path):
  return path.replace('\\', '/', -1)

def removeDir(dirPath):
  pathExists = os.path.exists(dirPath)
  if pathExists:
    shutil.rmtree(dirPath)

def makeDir(dirPath):
  pathExists = os.path.exists(dirPath)
  if not pathExists:
    os.mkdir(dirPath)

def utcTimeStringToLocalTimeString(utcTimeString, utcFormat, localFormat):
  utcTimeStruct = time.strptime(utcTimeString, utcFormat)
  timestamp = calendar.timegm(utcTimeStruct)
  localTimeStruct = time.localtime(timestamp)
  return time.strftime(localFormat, localTimeStruct)

def normalizeExifReadDateTime(dtString):
  return re.sub(r'^(\d{4}):(\d{2}):(\d{2})(.*)$', r'\g<1>-\g<2>-\g<3>\g<4>', dtString)

def normalizeMediaInfoDateTime(dtString):
  dt = dtString[-19:]
  if 'UTC' in dtString:
    dt = utcTimeStringToLocalTimeString(dt, r'%Y-%m-%d %H:%M:%S', r'%Y-%m-%d %H:%M:%S')
  return dt

def getImageInfo(filePath):
  info = {}
  with open(filePath, 'rb') as f:
    tags = exifread.process_file(f, details=False)
    imageDateTime = tags.get('EXIF DateTimeOriginal', '0')
    if imageDateTime == '0':
      imageDateTime = tags.get('EXIF DateTimeDigitized', '0')
    if imageDateTime != '0':
      imageDateTime = imageDateTime.values
      imageDateTime = normalizeExifReadDateTime(imageDateTime)
      info['recordTime'] = imageDateTime

  print(filePath, info['recordTime'])
  return info

def getVideoInfo(filePath):
  info = {}
  mediaInfo = MediaInfo.parse(filePath, full=False)
  jstring = mediaInfo.to_json()
  jdata = json.loads(jstring)
  videoDateTime = jdata['tracks'][0].get('encoded_date', '0')
  if videoDateTime == '0':
    videoDateTime = jdata['tracks'][0].get('tagged_date', '0')
  if videoDateTime != '0':
    videoDateTime = normalizeMediaInfoDateTime(videoDateTime)
    info['recordTime'] = videoDateTime

  print(filePath, info['recordTime'])
  return info

def visitFile(filePath):
  info = {}
  try:
    if re.search('.(jpg|png|heic)$', filePath, re.IGNORECASE) != None:
      info = getImageInfo(filePath)
    elif re.search('.(mp4|mov|avi|mp3|wav|aac|ogg)$', filePath, re.IGNORECASE) != None:
      info = getVideoInfo(filePath)
  except:
    exceptionalFiles.add(filePath)
  return info

def visitDir(basePath, relativePath):
  print('-----', basePath, relativePath, '-----', flush=True)

  global processedCount

  dirPath = joinPath(basePath, relativePath)

  baseMetaPath = joinPath(basePath, specificDir)
  dirMetaPath = baseMetaPath
  if mode == '0':
    dirMetaPath = joinPath(baseMetaPath, relativePath)
  if mode == '0' or relativePath == '':
    removeDir(dirMetaPath)
    makeDir(dirMetaPath)

  sdPaths = []
  sfPaths = []
  fileTagMap = {}
  unprocessedSet = set()

  for entryName in os.listdir(dirPath):
    result = re.search(r'({})$'.format(extensions), entryName, re.IGNORECASE)
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
    visitDir(basePath, sRelativePath)

  for sfPath in sfPaths:
    sFileName = sfPath[0]
    sFilePath = sfPath[1]
    fileInfo = visitFile(sFilePath)
    recordTime = fileInfo.get('recordTime', '0')
    if recordTime != '0':
      fileTag = recordTime[:10]
      filePathList = fileTagMap.setdefault(fileTag, [])
      filePathList.append(sFilePath)
      processedCount += 1
    else:
      unprocessedSet.add(sFilePath)
      unprocessedFiles.add(sFilePath)

  for fileTag, filePathList in fileTagMap.items():
    print(fileTag, len(filePathList), flush=True)

    tagMetaPath = joinPath(dirMetaPath, fileTag)
    print(tagMetaPath, flush=True)
    makeDir(tagMetaPath)

    for filePath in filePathList:
      fileRelatedPattern = re.sub(r'\.(\w+)$', '.*', filePath)
      for fileRelated in glob.glob(fileRelatedPattern):
        fileRelated = normalizePath(fileRelated)
        print('copy {} to {}'.format(fileRelated, tagMetaPath), flush=True)
        shutil.copy(fileRelated, tagMetaPath)
        unprocessedSet.discard(fileRelated)
        unprocessedFiles.discard(fileRelated)

    print('', flush=True)

  if len(unprocessedSet) > 0:
    unprocessedTag = '0'
    tagMetaPath = joinPath(dirMetaPath, unprocessedTag)
    print(tagMetaPath, flush=True)
    makeDir(tagMetaPath)
    for unprocessedFile in unprocessedSet:
        print('copy {} to {}'.format(unprocessedFile, tagMetaPath), flush=True)
        shutil.copy(unprocessedFile, tagMetaPath)

  print('', flush=True)

def visitInit(dirPath):
  print('visit Init: ', dirPath, flush=True)

  visitDir(dirPath, '')

  print('====================================================')
  print('Done! processed[{}] unprocessed[{}] exceptional[{}]'.format(processedCount, len(unprocessedFiles), len(exceptionalFiles)))
  print('')

  print('Unprocessed Files: ', flush=True)
  for unprocessedFile in unprocessedFiles:
    print('{}'.format(unprocessedFile))
  print('', flush=True)

  print('Exceptional Files: ', flush=True)
  for exceptionalFile in exceptionalFiles:
    print('{}'.format(exceptionalFile))
  print('', flush=True)

if __name__ == '__main__':
  dirPath = sys.argv[1]
  extensions = sys.argv[2]
  mode = sys.argv[3]

  visitInit(dirPath)
