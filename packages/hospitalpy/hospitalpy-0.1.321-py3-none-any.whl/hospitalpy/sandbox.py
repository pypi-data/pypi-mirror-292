import pandas as pd
import json
import os

from tqdm import tqdm
from config import ASSET_PATH
from Tokenizer import Tokenizer as Toker
from Evaluator import Evaluator as Evalor

# To gauge bulk performance
tqdm.pandas()

data = pd.read_excel(os.path.join(ASSET_PATH,'2nd round of iteration.xlsx'))
data = data[['source', 'original', 'standardized', 'change', 'needed', 'flag for review', 'notes']]

sample = data['original'].sample(10)

# Tokenize sample rows.
toker_list = [Toker(row) for row in sample]
for token in toker_list:
    print(f'Original String: {token.aStr}')
    print(f'Standardized String: {token.standardized}')

# # Bulk Conversion
# xf = data.copy(deep=True)
# xf['standardized'] = xf['original'].progress_apply(lambda x: Toker(x).standardized)

# Calculate Performance Metrics
# evil = Evalor()
#
# for toker in toker_list:
#     evil.evaluate_single(toker) # Default summarizes with no comparison to gold standard.

# Explain Processing

# Save to JSONL
SAVE_PATH = os.path.join(ASSET_PATH)
filename = 'test'
save_name = os.path.join(SAVE_PATH, f'{filename}.jsonl')
for toker in toker_list:
    with open(save_name, 'a') as f:
        f.write(toker.to_json())
        f.write('\n')
