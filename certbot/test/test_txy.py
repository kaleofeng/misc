#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from provider import txy

secret_id = 'NKIDXtLKJ7e55sW3B7rQmuXrzvfBTvAF0eu2'
secret_key = 'rhBMu6oVdkeKSN9ZloisOk03qRqmW7IO'

domain = 'metazion.org'
subdomain = 'apitest'
validation = 'VALIDATION_TEXT'

class TestProvider(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.provider = txy.Provider(secret_id, secret_key)

    def test_operation_record(self):
        record_id = self.provider._create_record(domain, subdomain, validation)
        print('创建解析记录：', record_id)
        self.assertGreater(record_id, 0)

        record_ids = self.provider._list_record(domain, subdomain)
        print('解析记录列表：', record_ids)
        self.assertEqual(len(record_ids), 1)

        delete_number = self.provider._delete_record(domain, record_id)
        print('删除解析记录：', delete_number)
        self.assertEqual(delete_number, 1)

if __name__ == '__main__':
    unittest.main()
