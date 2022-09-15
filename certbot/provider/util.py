# -*- coding: utf-8 -*-

import datetime
import random
import string
import time
from unittest import result

def normalize_dictionary(dict):
    """规格化数据，移除收尾空白，使全部小写，并按key字典升序排列数据."""

    result = lower_stripe_dictionary(dict)
    result = lexical_order_dictionary(result)
    return result

def lower_stripe_dictionary(dict):
    """规格化数据，移除收尾空白，并使全部小写."""

    result = {}
    for k, v in dict.items():
        key = k.strip().lower()
        value = v.strip().lower()
        result[key] = value

    return result

def lexical_order_dictionary(dict):
    """规格化数据，按key字典升序排列数据."""

    result = {}
    for k in sorted(dict.keys()):
        result[k] = dict[k]

    return result

def get_joined_key_string(dict, separator):
    """返回把key由分隔符连接的字符串."""

    return separator.join(dict.keys())

def get_joined_item_string(dict, separator):
    """返回把key=value由分隔符连接的字符串.."""

    units = []
    for k, v in dict.items():
        units.append('{}={}'.format(k, v))
    return separator.join(units)

def get_concat_item_string(dict, separator):
    """返回key:value分隔符为单元连接起来的字符串."""

    result = ''
    for k, v in dict.items():
        result += '{}:{}{}'.format(k, v, separator)
    return result

def get_timestamp_and_date():
    """获取时间戳和其对应日期."""

    timestamp = int(time.time())
    date = datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")
    return (timestamp, date)

def get_utc_datetime():
    """获取UTC日期时间."""

    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

def get_gmt_datetime():
    """获取GMT日期时间."""

    return datetime.datetime.utcnow().strftime('%a %d %b %Y %H:%M:%S GMT')

def generate_random_numeric(length):
    """生成指定长度的随机数值."""

    str_list = [random.choice(string.digits) for i in range(length)]
    return ''.join(str_list)
