#!/usr/bin/env python
#  -*- coding:utf-8 -*-

import io
import os
import pymysql
import sys
import time
import xlrd

def readFromFile(xlsName, records):
    wb = xlrd.open_workbook(xlsName)
    sheets = wb.sheets()
    sheet = sheets[0]

    timeString = xlsName[18:-4]
    timeArray = time.strptime(timeString, "%Y-%m-%d-%H-%M-%S")
    timestamp = int(time.mktime(timeArray))
    timestamp = timestamp - timestamp % 60

    nrows = sheet.nrows

    for i in range(1, nrows):
        row = sheet.row_values(i)
        record = {}
        record["album"] = int(row[0])
        record["sid"] = int(row[1])
        record["sname"] = row[2]
        record["todayPersons"] = int(row[3])
        record["totalPersons"] = int(row[4])
        record["totalAlbums"] = int(row[5])
        record["time"] = timestamp
        records.append(record)

    print("Read from file xls[%s] done" % xlsName)

def writeIntoDB(tableName, records):
    db = pymysql.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="album", charset="utf8mb4")
    cursor = db.cursor()

    # Write each record
    for record in records:
        sql = "INSERT INTO %s VALUES(0, '%d', '%d', '%s', '%d', '%d', '%d', '%d')" % (tableName, record["album"], record["sid"], record["sname"], record["todayPersons"], record["totalPersons"], record["totalAlbums"], record["time"])
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            db.rollback()
            print("Insert record[%d] error!" % record["sid"], e)

    db.close()
    print("Write into db table[%s] done" % tableName)

xlsDir = os.getcwd()
print(xlsDir)

for parent, dirnames, filenames in os.walk(xlsDir,  followlinks=True):
    for filename in filenames:
        if filename.find(".xls") >= 0:
            print(filename)

            records = []
            readFromFile(filename, records)

            print(records)
            writeIntoDB("tab_qmusic_singerstat", records)
