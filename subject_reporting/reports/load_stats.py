from __future__ import print_function
import os
import json


def load_stats(exp, subj):
    """
    Loads the stats dictionary from the target subject's JSON file.

    :param exp: The experiment to load stats from.
    :param subj: The subject to load stats from.
    :return: If the subject has a stats file, a dictionary containing those stats. Otherwise, returns False.
    """
    stat_dir = '/data/eeg/scalp/ltp/%s/behavioral/stats/' % exp
    data_file = os.path.join(stat_dir, 'stats_%s.json' % subj)
    if not os.path.exists(data_file):
        data_file = os.path.join(stat_dir, 'stats_%s_incomplete.json' % subj)
        if not os.path.exists(data_file):
            print('Warning: No stats file available for %s!' % subj)
            return False

    with open(data_file, 'r') as f:
        stats = json.load(f)

    return stats
