import os
import json
import numpy as np
import pylatex as ltx


def subject_report_ltpFR2(subj, stats=None):
    """
    TBA

    :param subj:
    :param stats:
    :return:
    """
    ###############
    #
    # Define parameters of experiment
    #
    ###############
    stat_dir = '/data/eeg/scalp/ltp/ltpFR2/behavioral/stats/'
    out_dir = '/data/eeg/scalp/ltp/ltpFR2/report/'

    ###############
    #
    # Load data if not provided
    #
    ###############
    if stats is None:
        # Data may either be in beh_data_LTP###.json or beh_data_LTP###_incomplete.json
        data_file = os.path.join(stat_dir, 'stats_%s.json' % subj)
        if not os.path.exists(data_file):
            data_file = os.path.join(stat_dir, 'stats_%s_incomplete.json' % subj)
            if not os.path.exists(data_file):
                return dict()
        with open(data_file, 'r') as f:
            stats = json.load(f)

    ###############
    #
    # Extract information from stats dictionary
    #
    ###############
    sessions = np.array(stats['session'])
    num_good_trials = np.array(stats['num_good_trials'])
    p_rec = np.array(stats['p_rec'])
    spc = np.array(stats['spc'])
    pfr = np.array(stats['pfr'])
    crp = np.array(stats['crp'])
    crl = np.array(stats['crl'])
    pli_perlist = np.array(stats['pli_perlist'])
    xli_perlist = np.array(stats['xli_perlist'])
    rep_perlist = np.array(stats['rep_perlist'])




    outfile = os.path.join(out_dir, '%s_report.pdf' % subj)
    return outfile


if __name__ == "__main__":
    s = input('Enter a subject ID: ')
    subject_report_ltpFR2(s)
