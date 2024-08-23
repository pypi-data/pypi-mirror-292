import itertools
import json
import logging
import os
from collections import defaultdict
from datetime import datetime

import more_itertools as mit
import regex as re

from .config import ASSET_PATH, LOG_PATH, TRANSLATION_TABLE

# Should store these separately, but how to deal with escape characters?

period_btw_letters = r'(?<=\w)\.(?=\w)'
period_beginning_or_ending_word = r'(?<=\s)\.|\.(?=\s)'

plus_btw_letters = r'(?<=\w)\+(?=\w)'
plus_beginning_or_ending_word = r'(?<=\s)\+|\+(?=\s)'

surrounding_punctuation = r'(?<=\w)[\.,\+\\\/\(\)]|[\.,\+\\\/\(\)](?=\w)'

letter = r'\b(\w+)\b'
delimiter = r'[\.,\+\\\/\(\)]'
two_letter_abbrev = r'\b' + letter + delimiter + letter
three_letter_abbrev = r'\b' + letter + delimiter + letter + delimiter + letter
pattern = r'(\w+(?:\s+\w+)*)(?:\b[' + delimiter + r']\b|$)'

def batched(iterable, n):
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError('n must be >= 1')
    it = iter(iterable)
    while (batch := list(itertools.islice(it, n))):
        yield batch
        
class Tokenizer:
    def __init__(self, aStr):

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filemode='w', level=logging.DEBUG, filename=os.path.join(LOG_PATH,f'{datetime.now().strftime("%m-%d-%Y")}.log'), format = '%(asctime)s: %(message)s')

        self.ttable = json.load(open(os.path.join(ASSET_PATH, TRANSLATION_TABLE)))
        try:
            self.aStr = aStr.lower()
        except AttributeError:
            msg = f'Input was {aStr}. Must be a string.'
            self.logger.error(msg)
            self.aStr = ""

        # Flatten translation table for performance.
        self.ttable_dict = {item['original']: item['standardized']
                            for item in self.ttable}

        self.json_repr = defaultdict(list)
        self.standardized, self.cleaned, self.unigrams = self.standardize()
        self.tokens = []
        self.standardized, self.cleaned, self.unigrams = self.standardize()


    def __repr__(self):
        return f'{self.aStr} -> {self.standardized}'

    def standardize(self):
        cleaned = re.sub(period_btw_letters, ' ', self.aStr)
        cleaned = re.sub(plus_btw_letters, ' ', cleaned)
        cleaned = re.sub(period_beginning_or_ending_word, '', cleaned)
        cleaned = re.sub(plus_beginning_or_ending_word, '', cleaned)
        cleaned = re.sub(surrounding_punctuation, '', cleaned)

        # Standardize unigrams
        unigrams = cleaned.split()
        for i, term in enumerate(unigrams):
            if term in self.ttable_dict:
                unigrams[i] = self.ttable_dict[term].strip()
                self.tokens.append({'original': term, 'modified': unigrams[i]})

        # Standardize bigrams
        standardized = ' '.join(unigrams)
        for bigram in batched(unigrams, 2):
            bigram = ' '.join(bigram)
            if bigram in self.ttable_dict:
                standardized.replace(bigram, self.ttable_dict[bigram])
                self.tokens.append({'original': bigram, 'modified': self.ttable_dict[bigram]})
        return (standardized, cleaned, unigrams)

    def tokenize(self):
        matches = re.findall(pattern, self.aStr)
        return list(matches)

    def to_json(self):
        return json.dumps({'original': self.aStr,
                           'standardized': self.standardized,
                           'tokens': self.json_repr})

__all__ = ['Tokenizer']
