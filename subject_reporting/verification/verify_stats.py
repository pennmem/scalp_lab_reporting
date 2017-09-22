import json
import numpy as np
from glob import glob
from scipy.io import loadmat
from subject_reporting.statistics.ltpFR2_stats import run_stats_ltpFR2


def verify_stats():
    datafiles = glob('/data/eeg/scalp/ltp/ltpFR2/behavioral/data/beh_data_LTP[0-9][0-9][0-9]*.json')

    for path in datafiles:
        with open(path) as f:
            data = json.load(f)
        subj = data['subject'][0]
        print(subj)

        stats = run_stats_ltpFR2(subj, data)

        try:
            matstat = loadmat('/data/eeg/scalp/ltp/ltpFR2/behavioral/stats/res_%s.mat' % subj)['res']
        except IOError:
            continue

        fields_to_check = [f for f in stats.keys() if f not in ('p_rec', 'crl')]
        try:
            for field in fields_to_check:
                new = np.array(stats[field])
                old = matstat[field][0][0] if field not in ('p_rec', 'pli_perlist', 'xli_perlist') else matstat[field][0][0].T
                match = ((new == old) | (np.isnan(new) & np.isnan(old))).all()
                if not match:
                    print(field)
        except:
            print('Unable to analyze %s!' % subj)


if __name__ == "__main__":
    verify_stats()
