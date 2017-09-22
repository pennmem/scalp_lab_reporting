import os
import json
import numpy as np
from pybeh.spc import spc
from pybeh.pfr import pfr
from pybeh.crp import crp
from pybeh.crl import crl
from pybeh.pli import pli
from pybeh.xli import xli
from pybeh.reps import reps
from subject_reporting.statistics.p_rec import p_rec


def run_stats_ltpFR2(subj, data=None):
    """
    TBA

    :param subj:
    :param data:
    :return:
    """

    ###############
    #
    # Define parameters of experiment
    #
    ###############
    data_dir = '/data/eeg/scalp/ltp/ltpFR2/behavioral/data/'
    out_dir = '/data/eeg/scalp/ltp/ltpFR2/behavioral/stats/'
    out_dir = '/Users/jessepazdera/Desktop/stats/'
    n_sess = 24

    ###############
    #
    # Load data if not provided
    #
    ###############
    if data is None:
        # Data may either be in beh_data_LTP###.json or beh_data_LTP###_incomplete.json
        data_file = os.path.join(data_dir, 'beh_data_%s.json' % subj)
        if not os.path.exists(data_file):
            data_file = os.path.join(data_dir, 'beh_data_%s_incomplete.json' % subj)
            if not os.path.exists(data_file):
                return dict()
        with open(data_file, 'r') as f:
            data = json.load(f)

    ###############
    #
    # Extract behavioral matrices, excluding bad trials
    #
    ###############
    good_trials = np.array(data['good_trial'])
    num_good_trials = good_trials.sum()
    # If all trials are bad, don't try to calculate stats
    if num_good_trials == 0:
        return dict()
    sessions = np.array(data['session'])[good_trials]
    recalled = np.array(data['recalled'])[good_trials]
    spos = np.array(data['serialpos'])[good_trials]
    times = np.array(data['times'])[good_trials]
    intru = np.array(data['intrusions'])[good_trials]
    recw = np.array(data['rec_words'])[good_trials]
    ll = np.array(data['pres_nos']).shape[1]

    ###############
    #
    # Run stats
    #
    ###############
    stats = dict()
    stats['p_rec'] = p_rec(recalled, sessions)
    stats['spc'] = spc(spos, sessions, ll)
    stats['pfr'] = pfr(spos, sessions, ll)
    stats['crp'] = crp(spos, sessions, ll, lag_num=ll - 1)
    stats['crl'] = crl(spos, times, sessions, ll, lag_num=ll - 1)
    stats['pli_perlist'] = pli(intru, sessions, recw, exclude_reps=True, per_list=True)
    stats['xli_perlist'] = xli(intru, sessions, recw, exclude_reps=True, per_list=True)
    stats['rep_perlist'] = reps(spos, sessions, unique_reps=False, per_list=True)

    ###############
    #
    # Save and return results
    #
    ###############
    # Convert numpy arrays to lists, so that they are JSON serializable
    for stat in stats:
        if isinstance(stats[stat], np.ndarray):
            stats[stat] = stats[stat].tolist()

    # Write stats to file, marking the file as incomplete if the participant has not completed all sessions
    complete = True if len(np.unique(data['session'])) == n_sess else False
    outfile = os.path.join(out_dir, 'stats_%s.json' % subj) if complete else os.path.join(out_dir, 'stats_%s_incomplete.json' % subj)
    with open(outfile, 'w') as f:
        json.dump(stats, f)

    return stats


if __name__ == "__main__":
    s = input('Enter a subject ID: ')
    run_stats_ltpFR2(s)
