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

specificDir= 'mzout'
specificNames = [os.path.basename(__file__), '.DS_Store']
print(specificNames)

extensions = '' # File extension list, e.g.: 'jpg|mp4|mov', empty for all extensions
mode = '0'      # Put all date directories to their respective directories or root directory 0:respective 1:root

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
    print('visit file caught exception', sys.exc_info())
  return info

def visitDir(basePath, relativePath):
  print('-----', basePath, relativePath, '-----')

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

    isSpecific = False
    for sn in specificNames:
      if entryName.endswith(sn):
        isSpecific = True
        break
    if isSpecific:
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
    print(fileTag, len(filePathList))

    tagMetaPath = joinPath(dirMetaPath, fileTag)
    print(tagMetaPath)
    makeDir(tagMetaPath)

    for filePath in filePathList:
      fileRelatedPattern = re.sub(r'\.(\w+)$', '.*', filePath)
      for fileRelated in glob.glob(fileRelatedPattern):
        fileRelated = normalizePath(fileRelated)
        print('copy {} to {}'.format(fileRelated, tagMetaPath))
        shutil.copy(fileRelated, tagMetaPath)
        unprocessedSet.discard(fileRelated)
        unprocessedFiles.discard(fileRelated)

    print('')

  if len(unprocessedSet) > 0:
    unprocessedTag = '0'
    tagMetaPath = joinPath(dirMetaPath, unprocessedTag)
    print(tagMetaPath)
    makeDir(tagMetaPath)
    for unprocessedFile in unprocessedSet:
        print('copy {} to {}'.format(unprocessedFile, tagMetaPath))
        shutil.copy(unprocessedFile, tagMetaPath)

def visitInit(dirPath):
  print('visit Init: ', dirPath)

  visitDir(dirPath, '')

  print('====================================================')
  print('Done! processed[{}] unprocessed[{}] exceptional[{}]'.format(processedCount, len(unprocessedFiles), len(exceptionalFiles)))
  print('')

  print('Unprocessed Files: ')
  for unprocessedFile in unprocessedFiles:
    print('{}'.format(unprocessedFile))
  print('')

  print('Exceptional Files: ')
  for exceptionalFile in exceptionalFiles:
    print('{}'.format(exceptionalFile))
  print('')

if __name__ == '__main__':
  print("usage: classify-files <target dir> <extensions> <mode>")
  print("e.g.: classify-files . 'jpg|mp4' 1")
  print("  target dir 要处理的目标目录，默认为当前目录")
  print("             Target directory, default current directory")
  print("  extensions 要处理的文件后缀列表，比如 'jpg|mp4|mov'，为空则处理所有后缀，默认为空")
  print("             File extension list, e.g.: 'jpg|mp4|mov', empty for all extensions, default empty")
  print("  mode       将生成的日期目录放到各自目录下还是根目录下, 0:各自目录 1:根目录，默认为0")
  print("             Put all date directories to their respective directories or root directory 0:respective 1:root, default 0")
  print("")

  dirPath = '.'
  extensions = ''
  mode = '0'

  argc = len(sys.argv)
  if argc >= 2:
    dirPath = sys.argv[1]
  if argc >= 3:
    extensions = sys.argv[2]
  if argc >= 4:
    mode = sys.argv[3]

  visitInit(dirPath)
