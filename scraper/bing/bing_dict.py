#!/usr/bin/env python
#  -*- coding:utf-8 -*-

import random
import re
import requests
from bs4 import BeautifulSoup

class WordInfo(object):
    def __init__(self, word):
        self.word = word
        self.pronunciations = []
        self.definitions = []
        self.examples = []

    def word_text(self):
        return self.word
    
    def pronunciation_text(self):
        ps = []
        for p in self.pronunciations:
            vs = [value for value in p.values()]
            ps.extend(vs)
        return '/{}/'.format('; '.join(ps))

    def definition_text(self):
        ds = []
        for d in self.definitions:
            dt = "[{}] {}".format(d['POS'], d['DEF'])
            ds.append(dt)
        return '\n'.join(ds)

    def example_text(self):
        es = []
        random_examples = self.examples
        if len(self.examples) >= 3:
            random_examples = random.sample(random_examples, 3)
        for i, e in enumerate(random_examples):
            et = "[{}] {}".format(i+1, e['EN'])
            es.append(et)
        return '\n'.join(es)

class DictExtractor(object):
    def __init__(self):
        self.url = 'https://www.bing.com/dict/search?q={word}'

    # 提取音标
    def extract_pronunciation(self, soup):
        pronunciations = []
        us_pron = soup.find('div', class_='hd_prUS')
        uk_pron = soup.find('div', class_='hd_pr')
        pattern = r'\[(.*?)\]'
        if us_pron:
            us_pron_text = us_pron.get_text(strip=True)
            match = re.search(pattern, us_pron_text)
            if match:
                pronunciations.append({'US': match.group(1)})
        if uk_pron:
            uk_pron_text = uk_pron.get_text(strip=True)
            match = re.search(pattern, uk_pron_text)
            if match:
                pronunciations.append({'UK': match.group(1)})
        return pronunciations

    # 提取词义
    def extract_definitions(self, soup):
        definitions = []
        pos_spans = soup.find_all('span', class_='pos')
        def_spans = soup.find_all('span', class_='def')
        for pos, definition in zip(pos_spans, def_spans):
            pos_text = pos.get_text()
            def_text = definition.get_text()
            definitions.append({'POS': pos_text, 'DEF': def_text})
        return definitions

    # 提取例句
    def extract_examples(self, soup):
        examples = []
        en_examples = soup.find_all('div', class_='sen_en')
        cn_examples = soup.find_all('div', class_='sen_cn')
        for en, cn in zip(en_examples, cn_examples):
            en_text = en.get_text()
            cn_text = cn.get_text()
            examples.append({'EN': en_text, 'CN': cn_text})
        return examples

    # 提取单词信息
    def extract_word(self, word):
        word_info = WordInfo(word)

        url = self.url.format(word=word)
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error response: {response.status_code}")
            return word_info
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        word_info.pronunciations = self.extract_pronunciation(soup)
        word_info.definitions = self.extract_definitions(soup)
        word_info.examples = self.extract_examples(soup)
        return word_info

# 测试示例
if __name__ == '__main__':
    word = 'within'
    bing_dict = DictExtractor()
    word_info = bing_dict.extract_word(word)
    print(word_info.word)
    print(word_info.word_text())
    print(word_info.pronunciations)
    print(word_info.pronunciation_text())
    print(word_info.definitions)
    print(word_info.definition_text())
    print(word_info.examples)
    print(word_info.example_text())