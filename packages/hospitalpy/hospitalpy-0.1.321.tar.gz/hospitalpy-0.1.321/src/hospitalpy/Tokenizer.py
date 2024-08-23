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
        self.tokens = self.tokenize()


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
        unstandardized = unigrams.copy()
        while len(unstandardized) > 0:
            print(f'Unstandardized: {unstandardized}')
            term = unstandardized.pop(0)
            print(f'Popped {term} from {unstandardized}')
            print(f'Checking {term} in self.ttable_dict: {term in self.ttable_dict}')
            if term in self.ttable_dict and term != self.ttable_dict[term]:
                # 2nd boolean term is a hack to prevent infinite loops. 
                # TODO: edit ttable so no entry has a key that is also its value.
                print(f'Replacing {term} with {self.ttable_dict[term]}')
                unigrams[unigrams.index(term)] = self.ttable_dict[term].strip()
                self.logger.info(f'Converted {term} to {self.ttable_dict[term]}')
                self.json_repr['unigrams'].append({'original':term, 'standardized': self.ttable_dict[term]})
                if self.ttable_dict[term] in self.ttable_dict:
                    print(f'Checking {self.ttable_dict[term]} in self.ttable_dict: {self.ttable_dict[term] in self.ttable_dict}')
                    unstandardized.insert(0, self.ttable_dict[term])

        # Standardize bigrams
        standardized = ' '.join(unigrams)
        for bigram in mit.windowed(unigrams, n=2, step=1):
            bigram = ' '.join([word for word in bigram if word is not None])
            if len(bigram.split())==2 and bigram in self.ttable_dict:
                standardized.replace(bigram, self.ttable_dict[bigram])
                self.json_repr['bigrams'].append({'original': bigram, 'standardized': self.ttable_dict[bigram]})
        if self.aStr != standardized:
            self.logger.info(f'Converted \n\t {self.aStr} to \n\t{standardized}')
        else:
            self.logger.info(f'No conversion performed for {self.aStr}')
        return (standardized, cleaned, unigrams)

    def tokenize(self):
        matches = re.findall(pattern, self.aStr)
        return list(matches)

    def to_json(self):
        return json.dumps({'original': self.aStr,
                           'standardized': self.standardized,
                           'tokens': self.json_repr})

__all__ = ['Tokenizer']
