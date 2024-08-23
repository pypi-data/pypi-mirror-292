import os

base_dir = os.path.dirname(os.path.abspath(__file__))
ASSET_PATH = os.path.join(base_dir, 'assets')
TRANSLATION_TABLE = 'translation_table.clinical_diagnosis.final.json'

LOG_PATH = os.path.join('./logs')
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)
