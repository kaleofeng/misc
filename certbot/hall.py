#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import importlib
import sys

secret_id = r'AKIDXtCKJ4e22sW3B7rQmuUrzvfBTvAF5ey4'
secret_key = r'yhBZu3oLdkeKSN5YloisOk02qRqmW1IO'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='对选择的域名解析服务商添加或删除解析记录')

    parser.add_argument(
        'opertion',
        help='add:添加一条记录 clear:删除所有记录')

    parser.add_argument(
        'provider',
        help='域名解析服务商名称，`provider`目录下需提供同名驱动脚本')

    parser.add_argument(
        'secret_id',
        help='域名解析服务商提供的API访问密钥ID')

    parser.add_argument(
        'secret_key',
        help='域名解析服务商提供的API访问密钥Key')

    parser.add_argument(
        'domain',
        help='要认证的主域名')

    parser.add_argument(
        'subdomain',
        help='要认证的子域名')

    parser.add_argument(
        'validation',
        help='要验证的文本')

    args = parser.parse_args()
    print('参数：', args)

    try:
        module_name = '{}.{}'.format('provider', args.provider)
        module = importlib.import_module(module_name)
        provider = module.Provider(args.secret_id, args.secret_key)
    except:
        print('Error: 没有找到域名解析服务商（{}）的驱动程序！'.format(args.provider))
        exit(-1)

    ac_domain = '{}.{}'.format('_acme-challenge', args.subdomain)
    subdomain = str.replace(ac_domain, '.' + args.domain, '')
    print('主域名：', args.domain)
    print('子域名：', subdomain)
    print('验证文本：', args.validation)

    if args.opertion == 'add':
        print('添加一条解析记录')
        result = provider.rcreate_one_record(args.domain, subdomain, args.validation)
    else:
        print('删除所有相关解析记录')
        result = provider.delete_all_record(args.domain, subdomain)

    print('操作结果：', result)
