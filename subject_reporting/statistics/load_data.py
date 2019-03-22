import os
import json


def load_data(exp, subj):
    """
    Loads the data dictionary from the target subject's JSON file.

    :param exp: The experiment to load data from.
    :param subj: The subject to load data from.
    :return: If the subject has a data file, a dictionary containing that info. Otherwise, returns False.
    """
    data_dir = '/data/eeg/scalp/ltp/%s/behavioral/data/' % exp
    data_file = os.path.join(data_dir, 'beh_data_%s.json' % subj)
    if not os.path.exists(data_file):
        data_file = os.path.join(data_dir, 'beh_data_%s_incomplete.json' % subj)
        if not os.path.exists(data_file):
            return False

    with open(data_file, 'r') as f:
        stats = json.load(f)

    return stats
