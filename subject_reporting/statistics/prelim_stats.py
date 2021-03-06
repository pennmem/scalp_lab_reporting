import os
import json
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from pybeh.spc import spc
from pybeh.pfr import pfr
from pybeh.crp import crp
from pybeh.crl import crl
from pybeh.pli import pli
from pybeh.xli import xli
from pybeh.reps import reps
from .blink_rate import calc_blink_rate
from .p_rec import p_rec
from .load_data import load_data


def serial_ratios(recalls, subjects, min_recs):
    """
    Calculates the proportion of trials on which participants initiated recall by recalling the first min_recs items
    presented on that trial in serial order. For instance, if min_recs = 4, trials where recall began recall with items
    1->2->3->4 will be considered serial recall. This function can be used to help check whether participants in free
    recall are rehearsing and performing serial recall instead.

    :param recalls: A trials x items matrix whose elements are the serial positions of recalled items.
    :param subjects: An array of identifier values indicating which subject (or session) each row of the recalls matrix
        originates from.
    :param min_recs: The minimum number of serial recalls that must be made on a trial to be counted as serial recall.
    :return: An array containing the fraction of trials on which each participant performed serial recall. Participants'
        results are sorted by alphabetical order if subject identifiers were strings, or numerical order if identifiers
        were integers.
    """
    if len(recalls) != len(subjects):
        raise Exception('Recalls matrix must have the same number of rows as subjects.')

    usub = np.unique(subjects)
    results = np.zeros(len(usub))

    # If min_recs is greater than the maximum number of recalls anyone made, just return an array of zeros.
    if min_recs > recalls.shape[1]:
        return results

    # Determine whether the first min_recs recalls in each trial matched the first min_recs words presented, in order.
    # In other words, word 1 should be recalled at index 0, word 2 should be recalled at index 1, etc.
    serial = np.ones(recalls.shape[0], dtype=bool)
    for i in range(min_recs):
        serial = serial & (recalls[:, i] == i + 1)

    # Calculate the proportion of trials from each subject that demonstrate serial recall
    for i, subj in enumerate(usub):
        results[i] = np.mean(serial[subjects == subj])

    return results


def run_stats_prelim(subj, data=None):
    """
    Runs a selection of statistics on the data from one prelim participant. Stats are returned in a dictionary mapping
    each stat's name to its results. The stats that are run for prelim participants are as follows:

    - Probability of Recall (p_rec)
    - Probability of First Recall (pfr)
    - Lag-Conditional-Response Probability (crp)
    - Lag-Conditional-Response Latency (crl)
    - Prior-List Intrusions (pli_perlist)
    - Extra-List Intrusions (xli_perlist)
    - Repetitions (rep_perlist)
    - Blink Rate (blink_rate)

    An array called num_good_trials is also added to the dictionary, which indicates how many trials from each session
    were used to generate the stats for that session. Lastly, an array called session indicates which session each row
    of stats came from.

    After saving the statistics to a JSON file, this function proceeds to plot the SPC, PFR, and CRP for use on a
    subject report.

    :param subj: A string containing the subject ID for a participant.
    :param data: Optional. A dictionary containing the behavioral matrices generated by behavioral_matrices_prelim. If
    None, loads the data from /data/eeg/scalp/ltp/prelim/behavioral/data/beh_data_LTP*.json.
    :return: A dictionary containing the results of each analysis for the specified participant.
    """

    ###############
    #
    # Define parameters of experiment
    #
    ###############
    exp = 'prelim'
    out_dir = '/data/eeg/scalp/ltp/%s/behavioral/stats/' % exp
    n_sess = 1

    ###############
    #
    # Load data if not provided
    #
    ###############
    if data is None:
        data = load_data(exp, subj)
        if not data:
            return dict()

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
    recalls = np.array(data['recalls'])[good_trials]
    times = np.array(data['times'])[good_trials]
    intru = np.array(data['intrusions'])[good_trials]
    recw = np.array(data['rec_words'])[good_trials]
    blinks = np.array(data['blinks'])
    ll = np.array(data['pres_nos']).shape[1]
    # If participant never made any recalls, don't try to calculate stats
    if recw.shape[1] == 0:
        return dict()

    ###############
    #
    # Run stats
    #
    ###############
    stats = dict()
    stats['session'] = np.unique(sessions)
    stats['num_good_trials'] = [int(np.sum(sessions == i)) for i in np.unique(sessions)]
    stats['p_rec'] = p_rec(recalled, sessions)
    stats['spc'] = spc(recalls, sessions, ll)
    stats['pfr'] = pfr(recalls, sessions, ll)
    stats['crp'] = crp(recalls, sessions, ll, lag_num=ll - 1)
    stats['crl'] = crl(recalls, times, sessions, ll, lag_num=ll - 1)
    stats['pli_perlist'] = pli(intru, sessions, recw, exclude_reps=True, per_list=True)
    stats['xli_perlist'] = xli(intru, sessions, recw, exclude_reps=True, per_list=True)
    stats['rep_perlist'] = reps(recalls, sessions, unique_reps=False, per_list=True)
    stats['blink_rate'] = calc_blink_rate(blinks, sessions)
    stats['serial_ratio'] = serial_ratios(recalls, sessions, min_recs=4)

    ###############
    #
    # Save results
    #
    ###############
    # Convert numpy arrays to lists, so that they are JSON serializable
    for stat in stats:
        if isinstance(stats[stat], np.ndarray):
            stats[stat] = stats[stat].tolist()

    # Write stats to file, marking the file as incomplete if the participant has not completed all sessions
    complete = True if len(np.unique(data['session'])) == n_sess else False
    outfile_complete = os.path.join(out_dir, 'stats_%s.json' % subj)
    outfile_incomplete = os.path.join(out_dir, 'stats_%s_incomplete.json' % subj)

    # Save data as a json file with one of two names, depending on whether the participant has finished all sessions
    if complete:
        with open(outfile_complete, 'w') as f:
            json.dump(stats, f)
        # After the person runs their final session, we can remove the old data file labelled with "incomplete"
        if os.path.exists(outfile_incomplete):
            os.remove(outfile_incomplete)
    else:
        with open(outfile_incomplete, 'w') as f:
            json.dump(stats, f)

    ###############
    #
    # Plot Performance Stats
    #
    ###############
    matplotlib.rc('font', size=36)  # default text sizes
    matplotlib.rc('axes', titlesize=36)  # fontsize of the axes title
    matplotlib.rc('axes', labelsize=36)  # fontsize of the x and y labels
    matplotlib.rc('xtick', labelsize=36)  # fontsize of the x-axis tick labels
    matplotlib.rc('ytick', labelsize=36)  # fontsize of the y-axis tick labels
    matplotlib.rc('figure', titlesize=40)  # fontsize of the figure title

    fig_dir = '/data/eeg/scalp/ltp/prelim/%s/figs/' % subj
    if not os.path.exists(fig_dir):  # Make sure figure directory exists
        os.mkdir(fig_dir)

    ###############
    #
    # Plot Recall Stats
    #
    ###############
    matplotlib.rc('font', size=22)  # default text sizes
    matplotlib.rc('axes', titlesize=22)  # fontsize of the axes title
    matplotlib.rc('axes', labelsize=22)  # fontsize of the x and y labels
    matplotlib.rc('xtick', labelsize=24)  # fontsize of the x-axis tick labels
    matplotlib.rc('ytick', labelsize=24)  # fontsize of the y-axis tick labels
    matplotlib.rc('figure', titlesize=22)  # fontsize of the figure title

    # Average SPC
    s = stats['spc']
    fig = plt.figure()
    plt.plot(range(1, ll + 1), np.mean(s, axis=0), '-ko')
    plt.title('%s -- Average' % subj)
    plt.xlabel('Serial Position')
    plt.ylabel('Recall Probability')
    plt.xlim(.5, ll+.5)
    plt.ylim(0, 1)
    plt.xticks([1, 4, 8, 12, 15])
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'spc.pdf'))
    plt.close(fig)

    # Average PFR
    s = stats['pfr']
    fig = plt.figure()
    plt.plot(range(1, ll + 1), np.mean(s, axis=0), '-ko')
    plt.title('%s -- Average' % subj)
    plt.xlabel('Serial Position')
    plt.ylabel('Probability of First Recall')
    plt.xlim(.5, ll+.5)
    plt.ylim(0, 1)
    plt.xticks([1, 4, 8, 12, 15])
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'pfr.pdf'))
    plt.close(fig)

    # Average CRP
    s = stats['crp']
    lag_num = 6
    fig = plt.figure()
    plt.plot(range(-lag_num, lag_num + 1), np.mean(s, axis=0)[ll - lag_num - 1:ll + lag_num], '-ko')
    plt.title('%s -- Average' % subj)
    plt.xlabel('Lag')
    plt.ylabel('Cond. Resp. Probability')
    plt.ylim(0, 1)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'crp.pdf'))
    plt.close(fig)

    return stats


if __name__ == "__main__":
    s = input('Enter a subject ID: ')
    run_stats_prelim(s)
