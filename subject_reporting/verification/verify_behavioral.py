from glob import glob
import json
from scipy.io import loadmat
import numpy as np


fields_to_check = (('rec_nos', 'rec_itemnos'), ('pres_nos', 'pres_itemnos'), ('serialpos', 'recalls'), ('times', 'times'), ('intrusions', 'intrusions'), ('recalled', 'recalled'))

files = glob('/Users/jessepazdera/Desktop/behavioral/beh_data_LTP[0-9][0-9][0-9].json')
for path in files:
    with open(path) as f:
        data = json.load(f)
    subj = data['subject'][0]
    print(subj)

    try:
        matdata = loadmat('/data/eeg/scalp/ltp/ltpFR2/behavioral/data/stat_data_%s.mat' % subj)['data']
    except IOError:
        continue

    try:
        for field in fields_to_check:
            match = (data[field[0]] == matdata[field[1]][0][0].tolist()) if field[0] != "recalled" else (data[field[0]] == matdata['pres'][0][0][field[1]][0][0].tolist())
            if not match:
                print(field)
    except:
        print('Unable to analyze %s!' % subj)
