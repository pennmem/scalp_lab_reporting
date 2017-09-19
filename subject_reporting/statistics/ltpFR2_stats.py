import os
import json
import numpy as np
from pybeh.spc import spc
from pybeh.pnr import pnr
from pybeh.crp import crp
from pybeh.irt import irt
from pybeh.crl import crl
from pybeh.custom.prec import prec
from pybeh.custom.avg_pli import avg_pli
from pybeh.custom.avg_eli import avg_eli
from pybeh.custom.avg_reps import avg_reps
# from pybeh.temp_fact import temp_fact
# from pybeh.dist_fact import dist_fact
# from pybeh.sem_crp import sem_crp
# from scipy.io import loadmat


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
    # pres_nos = np.array(data['pres_nos'])[good_trials]
    # rec_nos = np.array(data['rec_nos'])[good_trials]
    # lsa = loadmat('pybeh/LSA.mat')['LSA']

    ###############
    #
    # Run stats
    #
    ###############
    stats = dict()
    stats['prec'] = prec(recalled, sessions)
    stats['spc'] = spc(spos, sessions, ll)
    stats['pfr'] = pnr(spos, sessions, ll, n=0)
    stats['psr'] = pnr(spos, sessions, ll, n=1)
    stats['ptr'] = pnr(spos, sessions, ll, n=2)
    stats['crp'] = crp(spos, sessions, ll, lag_num=ll - 1)
    stats['crl'] = crl(spos, times, sessions, ll, lag_num=ll - 1)
    stats['irt'] = irt(times)
    stats['pli_perlist'] = avg_pli(intru, sessions, recw)
    stats['eli_perlist'] = avg_eli(intru, sessions)
    stats['reps_perlist'] = avg_reps(spos, sessions)
    # stats['temp_fact'] = temp_fact(spos, sessions, ll)
    # stats['dist_fact'] = dist_fact(rec_nos, pres_nos, sessions, lsa, ll)
    # stats['sem_crp'] = sem_crp(spos, rec_nos, pres_nos, sessions, lsa, 10, ll)
    # stats['pli_recency'] = nback_pli(intru, sessions, 6, recw)[0]

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
