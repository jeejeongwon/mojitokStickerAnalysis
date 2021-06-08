import pandas as pd
import numpy as np
import urllib
import sqlite3
import re
import pickle
from preprocess import get_cs_query_dict, load_and_parse_data, load_db_info, tag_inference, transform_data
from model import em_algorithm_inference

try:
    with open('./data/preprocessed.pickle', 'rb') as f:
        preprocessed = pickle.load(f)
except:
    data_path = ''
    db_path = ''
    parsed = load_and_parse_data(data_path)
    s2e = load_db_info(db_path)
    inferenced = tag_inference(parsed, s2e)
    preprocessed = transform_data(inferenced)

result = em_algorithm_inference(data, seed_num=2021)
print(result['theta_k'])
print(result['gamma_qd'])

with open('./data/model_result.pickle', 'wb') as f:
    pickle.dump(result, f, pickle.HIGHEST_PROTOCOL)