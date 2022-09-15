# -*- coding: utf-8 -*-

import hashlib
import hmac
import json
import urllib.request

from provider import util

def _get_authorization_header(secret_id, secret_key, service, header, payload, timestamp, date):
    # 0. 规格化数据
    normalized_header = util.normalize_dictionary(header)
    payload_string = json.dumps(payload)

    # 1. 拼接规范请求串
    HTTPRequestMethod = 'POST'
    CanonicalURI = '/'
    CanonicalQueryString = ''
    CanonicalHeaders = util.get_concat_item_string(normalized_header, '\n')
    SignedHeaders = util.get_joined_key_string(normalized_header, ';')
    HashedRequestPayload = hashlib.sha256(payload_string.encode('utf-8')).hexdigest().lower()

    items = []
    items.append(HTTPRequestMethod)
    items.append(CanonicalURI)
    items.append(CanonicalQueryString)
    items.append(CanonicalHeaders)
    items.append(SignedHeaders)
    items.append(HashedRequestPayload)
    CanonicalRequestString = '\n'.join(items)

    # 2. 拼接待签名字符串
    Algorithm = 'TC3-HMAC-SHA256'
    RequestTimestamp = str(timestamp)
    CredentialScope = '{}/{}/{}'.format(date, service, 'tc3_request')
    HashedCanonicalRequest = hashlib.sha256(CanonicalRequestString.encode('utf-8')).hexdigest().lower()

    items = []
    items.append(Algorithm)
    items.append(RequestTimestamp)
    items.append(CredentialScope)
    items.append(HashedCanonicalRequest)
    ToSignString = '\n'.join(items)

    # 3. 计算签名
    key = ('TC3' + secret_key).encode('utf-8')
    SecretDate = hmac.new(key, date.encode('utf-8'), digestmod=hashlib.sha256).digest()
    SecretService = hmac.new(SecretDate, service.encode('utf-8'), digestmod=hashlib.sha256).digest()
    SecretSigning = hmac.new(SecretService, 'tc3_request'.encode('utf-8'), digestmod=hashlib.sha256).digest()
    SecretSigningBytes = SecretSigning

    SignatureString = hmac.new(SecretSigningBytes, ToSignString.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()

    # 4. 拼接 Authorization
    Algorithm = Algorithm
    Credential = '{}/{}'.format(secret_id, CredentialScope)
    SignedHeaders = SignedHeaders
    Signature = SignatureString
    Authorization = '{} Credential={}, SignedHeaders={}, Signature={}'.format(Algorithm, Credential, SignedHeaders, Signature)

    # 装配Header
    normalized_header['Authorization'] = Authorization
    return normalized_header

def _do_post(secret_id, secret_key, service, header, payload, action):
    # 生成带有认证的Header
    timestamp, date = util.get_timestamp_and_date()
    real_header = _get_authorization_header(secret_id, secret_key, service, header, payload, timestamp, date)

    # 公共参数
    real_header['X-TC-Action'] = action
    real_header['X-TC-Version'] = '2021-03-23'
    real_header['X-TC-Timestamp'] = str(timestamp)
    real_header['X-TC-Region'] = ''

    # 发起请求
    url = 'https://dnspod.tencentcloudapi.com'
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=real_header, method='POST')
    with urllib.request.urlopen(req) as f:
        return json.loads(f.read())

class Provider:
    """域名解析服务商驱动程序."""

    def __init__(self, secret_id, secret_key) -> None:
        self.name = 'txy'
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.service = 'dnspod'
        self.header = {
            'content-type': 'application/json; charset=utf-8',
            'host': 'dnspod.tencentcloudapi.com',
        }

    def name(self):
        """返回Provider的名称."""

        return self.name

    def rcreate_one_record(self, domain, subdomain, value):
        """添加一条解析记录."""

        record_id = self._create_record(domain, subdomain, value)
        return record_id != ''

    def delete_all_record(self, domain, subdomain):
        """删除所有相关解析记录."""

        record_ids = self._list_record(domain, subdomain)
        for record_id in record_ids:
            self._delete_record(domain, record_id)
        return True

    def _create_record(self, domain, subdomain, value):
        payload = {
            'Domain': domain,
            'SubDomain': subdomain,
            'RecordType': 'TXT',
            'RecordLine': '默认',
            'Value': value
        }

        rsp_data = _do_post(self.secret_id, self.secret_key, self.service, self.header, payload, 'CreateRecord')
        if self._check_response_error(rsp_data):
            return ''

        record_id = rsp_data['Response']['RecordId']
        return record_id

    def _delete_record(self, domain, record_id):
        payload = {
            'Domain': domain,
            'RecordId': record_id
        }

        rsp_data = _do_post(self.secret_id, self.secret_key, self.service, self.header, payload, 'DeleteRecord')
        if self._check_response_error(rsp_data):
            return 0

        return 1

    def _list_record(self, domain, subdomain):
        payload = {
            'Domain': domain,
            'Subdomain': subdomain,
            'RecordType': 'TXT',
            'RecordLine': '默认',
        }

        rsp_data = _do_post(self.secret_id, self.secret_key, self.service, self.header, payload, 'DescribeRecordList')
        if self._check_response_error(rsp_data):
            return []

        record_ids = []
        for record in rsp_data['Response']['RecordList']:
            record_ids.append(record['RecordId'])
        return record_ids

    def _check_response_error(self, rsp_data):
        if 'Error' in rsp_data['Response']:
            err_code = rsp_data['Response']['Error']['Code']
            err_msg = rsp_data['Response']['Error']['Message']
            print("Error: {}:{}".format(err_code, err_msg))
            return True
        return False
