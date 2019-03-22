import os
import json
import numpy as np
from .load_data import load_data
# import matplotlib
# matplotlib.use('agg')
# import matplotlib.pyplot as plt
# from pandas import read_csv


def run_stats_VFFR(subj, data=None):
    """
    Runs a selection of statistics on the data from one VFFR participant. Stats are run separately for each of that
    participant's sessions, and are returned in a dictionary mapping each stat's name to its results. The stats that
    are run for VFFR participants are as follows:

    - Total correct recalls (recalls)
    - Total intrusions (intrusions) -- Note that only ELIs are possible in VFFR
    - Total repetitions (repetitions) -- Note that this counts the number of repetitions of correct words; repeated ELIs
        contribute instead ot the ELI count

    Two arrays called subject and session are also added to the dictionary, which indicate the subject and  session from
    which each stat entry originates. The dictionary is saved to a JSON file and plots are generated for use on a
    subject report.

    :param subj: A string containing the subject ID for a participant.
    :param data: Optional. A dictionary containing the behavioral matrices generated by behavioral_matrices_ltpFR2. If
    None, loads the data from /data/eeg/scalp/ltp/VFFR/behavioral/data/beh_data_<subj>.json.
    :return: A dictionary containing the results of each analysis for the specified participant.
    """

    ###############
    #
    # Define parameters of experiment
    #
    ###############
    exp = 'VFFR'
    # bonus_dir = '/data/eeg/scalp/ltp/%s/bonus/' % exp
    out_dir = '/data/eeg/scalp/ltp/%s/behavioral/stats/' % exp
    n_sess = 10

    ###############
    #
    # Load data if not provided
    #
    ###############
    if data is None:
        data = load_data(exp, subj)
        if not data:
            return dict()

    # Load bonus data so we can plot blink rates
    # bonus_data = None
    # bonus_data_file = os.path.join(bonus_dir, '%s_bonus_report.tsv' % subj)
    # if os.path.exists(bonus_data_file):
    #     bonus_data = read_csv(bonus_data_file, delimiter='\t')

    ###############
    #
    # Extract behavioral matrices, excluding bad trials
    #
    ###############
    sessions = np.array(data['session'])
    recalled = np.array(data['recalled'])
    intru = np.array(data['intrusions'])
    recs = np.array(data['rec_words'])

    ###############
    #
    # Run stats
    #
    ###############
    stats = dict()
    stats['session'] = np.unique(sessions)
    stats['subject'] = np.array([subj] * len(stats['session']))
    stats['recalls'] = np.nansum(recalled, axis=1)
    # There are no PLIs, so sum of intru is -1 * number of ELIs; remove the negative to get total number of ELIs
    stats['intrusions'] = np.nansum(intru, axis=1) * -1
    # Count repetitions of correct recalls (i.e. if the word was recalled earlier and is not an intrusion)
    stats['repetitions'] = np.zeros(len(stats['session']), dtype=float)
    for sess, sess_data in enumerate(recs):
        if np.all(np.isnan(recalled[sess, :])):
            stats['recalls'][sess] = np.nan
            stats['intrusions'][sess] = np.nan
            stats['repetitions'][sess] = np.nan
        else:
            for i, w in enumerate(sess_data):
                if w != '' and np.isin(w, sess_data[:i]) and intru[sess, i] == 0:
                    stats['repetitions'][sess] += 1

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

    """
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

    fig_dir = '/data/eeg/scalp/ltp/ltpFR2/%s/figs/' % subj
    if not os.path.exists(fig_dir):  # Make sure figure directory exists
        os.mkdir(fig_dir)

    # PRec over sessions; include faint lines to indicate where tiers of bonus payments begin and end
    fig = plt.figure(figsize=(26, 24))
    plt.subplot(321)
    s = np.empty(n_sess)
    s.fill(np.nan)
    s[:len(stats['p_rec'])] = stats['p_rec']
    plt.plot(range(0, n_sess), s, 'ko', markersize=15)
    plt.axhline(np.nanmean(s), linestyle='--', color='k', linewidth=3)
    plt.title('Recall Probability')
    plt.xlim(-1, 25)
    plt.ylim(0, 1)
    plt.xticks([0, 6, 12, 18, 24])

    # Blink rate over sessions
    plt.subplot(323)
    s = [x.split('/')[2][:-1] for x in bonus_data['Blink Rate'][:-1]]
    s = [np.nan if x == '' else x for x in s]
    s = np.array(s, dtype=float) / 100
    plt.plot(range(0, n_sess), s, 'ko', markersize=15)
    plt.axhline(np.nanmean(s), linestyle='--', color='k', linewidth=3)
    plt.title('Blink Rate')
    plt.xlim(-1, 25)
    plt.ylim(0, 1)
    plt.xticks([0, 6, 12, 18, 24])

    # ELI over sessions
    plt.subplot(324)
    s = np.empty(n_sess)
    s.fill(np.nan)
    s[:len(stats['xli_perlist'])] = stats['xli_perlist']
    plt.plot(range(0, n_sess), s, 'ko', markersize=15)
    plt.axhline(np.nanmean(s), linestyle='--', color='k', linewidth=3)
    plt.title('ELIs')
    plt.xlim(-1, 25)
    plt.ylim(-0.05, max(s) + .1)
    plt.xticks([0, 6, 12, 18, 24])

    # Reps over sessions
    plt.subplot(326)
    s = np.empty(n_sess)
    s.fill(np.nan)
    s[:len(stats['rep_perlist'])] = stats['rep_perlist']
    plt.plot(range(0, n_sess), s, 'ko', markersize=15)
    plt.axhline(np.nanmean(s), linestyle='--', color='k', linewidth=3)
    plt.xlabel('Session Number')
    plt.title('Repetitions')
    plt.xlim(-1, 25)
    plt.ylim(-0.05, max(s) + .1)
    plt.xticks([0, 6, 12, 18, 24])

    plt.tight_layout(w_pad=2.5, h_pad=3.75)
    fig.savefig(os.path.join(fig_dir, 'performance.pdf'))
    #fig.savefig(os.path.join('/Users/jpazdera/Desktop/performance.pdf'))
    plt.close(fig)
    """

    return stats


if __name__ == "__main__":
    s = input('Enter a subject ID: ')
    run_stats_VFFR(s)
