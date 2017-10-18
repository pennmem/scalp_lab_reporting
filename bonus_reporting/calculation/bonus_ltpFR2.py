import os
import csv
import numpy as np
from ptsa.data.readers import BaseEventReader


def calculate_prec(events, return_percent=False):
    """
    Calculates a participant's probability of recall based on their events structure. Any words lacking recall
    information are excluded from the calculation.

    :param events: An events structure
    :param return_percent: If true, returns the prec as a percentage. If false, returns the prec as a ratio.
    (Default = False)
    :return: The participant's probability of recall, or np.nan if no recall information was available.
    """
    # Get only word presentation events with info on whether they were recalled
    pres_events = events[np.logical_and(events['type'] == 'WORD', np.logical_not(np.isnan(events['recalled'])))]
    # Count number of word presentations with recall info
    total_pres = pres_events.shape[0]
    # If no words have recall info, prec cannot be calculated
    if total_pres == 0:
        return np.nan
    # Calculate probability of recall across entire session
    prec = np.sum(pres_events['recalled']) / total_pres if total_pres > 0 else np.nan
    # Convert probability of recall to a percentage if specified
    prec = prec * 100 if return_percent else prec
    return prec


def calculate_blink_rate(events, pres_duration, return_percent=False):
    """
    Calculates a participant's blink rate based on an events structure. This requires alignment and blink detection to
    have already been run on the session's EEG data. The blink rate is defined as the fraction of presentation events
    during which the participant blinked or showed other EOG artifacts while the presented item was on the screen. For
    sessions where some presentation events lack EEG data, only the presentation events with artifactMS info are
    included in the calculation.

    :param events: An events structure
    :param pres_duration: The number of milliseconds for which each item was presented on the screen (1600 for ltpFR2)
    :param return_percent: If true, returns the blink rate as a percentage. If false, returns the blink rate as a ratio.
    :return: The participant's blink rate, or np.nan if no artifactMS information was available.
    """
    # If blink detection has not been run for this session, blink rate cannot be calculated
    if 'artifactMS' not in events.dtype.fields:
        return np.nan
    # Get only word presentation events with eeg
    pres_events = events[np.logical_and(events['type'] == 'WORD', np.logical_not(events['eegfile'] == ''))]
    # Count number of word presentations with artifactMS info
    total_pres = float(pres_events.shape[0])
    # If there are no presentation events with artifactMS info, blink rate cannot be calculated
    if total_pres == 0:
        return np.nan
    # Count number of word presentations where the participant blinked while the word was on the screen
    pres_with_blink = pres_events[np.logical_and(pres_events['artifactMS'] >= 0, pres_events['artifactMS'] <= pres_duration)].shape[0]
    # Calculate blink rate as presentations with blinks / total presentations
    br = pres_with_blink / total_pres if total_pres > 0 else np.nan
    # Convert blink rate to a percentage if specified
    br = br * 100 if return_percent else br
    return br


def get_math_correct(subj, sess):
    """
    Looks up a participant's math score from a single session by accessing their session log. The total math score for
    each session should be listed near the end of that session's log. If no score can be found in the session log or no
    session log exists, returns np.nan.

    :param subj: The subject ID of the target participant
    :param sess: The session number, as an integer (0-indexed)
    :return: The total number of math questions the participant answered correctly during the specified session, or
    np.nan if the math score cannot be found.
    """
    # Load the session log from that session
    session_log = '/data/eeg/scalp/ltp/ltpFR2/%s/session_%d/session.log' % (subj, sess)
    if os.path.exists(session_log):
        with open(session_log, 'r') as f:
            sess_log = list(csv.reader(f, delimiter='\t'))
        # Find the row that lists the total math score at the end of the session, and extract the math score from it
        total = [r[3] for r in sess_log if len(r) >= 4 and r[2] == 'MATH_TOTAL_SCORE']
        mc = int(total[-1]) if len(total) > 0 else np.nan
    else:
        mc = np.nan
    return mc


def calculate_bonus_ltpFR2(subj):
    """
    Calculates bonus payments for each of a participant's 24 sessions based on the following performance brackets:

    P-Recs:
    $0 --> 0% - 19.99%
    $1 --> 20% - 29.99%
    $2 --> 30% - 39.99%
    $3 --> 40% - 49.99%
    $4 --> 50% - 69.99%
    $5 --> 70% - 100%

    Blink rates:
    $0 --> > 50%
    $1 --> 40% - 49.99%
    $2 --> 30% - 39.99%
    $3 --> 20% - 29.99%
    $4 --> 10% - 19.99%
    $5 --> 0% - 9.99%

    Math Correct:
    $0 --> < 200
    $1 --> 200 - 349
    $2 --> 350 - 399
    $3 --> 400 - 449
    $4 --> 450 - 499
    $5 --> > 500

    Recall scores and bonuses can only be calculated once the session has been annotated. Blink rates can only be
    calculated if the session has been successfully aligned and blink detection has been run. If not all presentation
    events have EEG data, the blink rate is calculated only over the events that do.

    :param subj: A string containing the subject ID of the participant for whom to calculate bonuses.
    :return: Returns two numpy arrays. The first is a session x score matrix, with prec in column 0, blink rate in
    column 1, and math score in column 2. The second is a session x bonus matrix, with recall bonus in column 0, blink
    bonus in column 1, math bonus in column 2, and total bonus in column 3.
    """

    # Set experiment parameters and performance bracket boundaries
    n_sessions = 24
    pres_duration = 1600
    brackets = dict(
        prec=[20, 30, 40, 50, 70],
        br=[10, 20, 30, 40, 50],
        mc=[200, 350, 400, 450, 500]
    )

    scores = np.zeros((24, 3))
    bonuses = np.zeros((24, 4))
    # Calculate scores and bonuses for each session
    for sess in range(n_sessions):
        # If session has exists and has been post-processed, calculate prec and blink rate, otherwise, set as nan
        event_file = '/data/eeg/scalp/ltp/ltpFR2/%s/session_%d/events.mat' % (subj, sess)
        if not os.path.exists(event_file):  # Look for the MATLAB event file if we can't find the JSON one
            event_file = '/protocols/ltp/subjects/%s/experiments/ltpFR2/sessions/%d/behavioral/current_processed/task_events.json' % (subj, sess)
        if not os.path.exists(event_file):
            prec = np.nan
            br = np.nan
        else:
            # Load events for given subejct and session
            ev = BaseEventReader(filename=event_file, common_root='data', eliminate_nans=False, eliminate_events_with_no_eeg=False).read()

            # Calculate performance from the target session
            prec = calculate_prec(ev, return_percent=True)
            br = calculate_blink_rate(ev, pres_duration, return_percent=True)

        # Math score can be calculated even before the session has been post-processed, as it only relies on the log
        mc = get_math_correct(subj, sess)

        # Calculate bonuses based on performance brackets
        prec_bonus = np.searchsorted(brackets['prec'], prec, side='right') if not np.isnan(prec) else np.nan
        blink_bonus = 5 - np.searchsorted(brackets['br'], br, side='right') if not np.isnan(br) else np.nan
        math_bonus = np.searchsorted(brackets['mc'], mc, side='right') if not np.isnan(mc) else np.nan
        total_bonus = prec_bonus + blink_bonus + math_bonus

        # Record scores and bonuses from session
        scores[sess] = [prec, br, mc]
        bonuses[sess] = [prec_bonus, blink_bonus, math_bonus, total_bonus]

    return scores, bonuses


'''
from scipy.io import loadmat
from scipy.stats import percentileofscore
from glob import glob

def calculate_bonus_ltpFR2_continuous(subj_list, sess_list):
    """
    Calculate bonus payments based on a participant's percentile rank among all sessions ever run. Not currently used,
    but was implemented in case we wish to move from performance brackets to a continuous function. To use, it will need
    to be revised to fit with newer versions of the ltpFR2 bonus reporting script.3333
    """

    if len(subj_list) != len(sess_list):
        print 'subj_list and sess_list parameters must be the same length!'

    # Set experiment parameters
    pres_duration = 1600

    # Load performance scores from all past subjects and sessions
    precs = []
    blink_rates = []
    math_correct = []

    res_files = glob('/data/eeg/scalp/ltp/ltpFR2/behavioral/stats/res_LTP*')
    print '%d res structures found!' % len(res_files)

    for f in res_files:
        res = loadmat(f, squeeze_me=True)['res']
        if res is None:
            print 'Bad file: %s' % f
            continue

        # Extract the stats table that is written on subject reports, then pull the PRec, blink rate, and math correct
        res = np.array(res['stats_table_cell_all'].tolist().tolist()[1:], dtype=float)
        precs += [n for n in res[:, 1] if not np.isnan(n)]
        blink_rates += [n for n in res[:, 10] if not np.isnan(n)]
        math_correct += [n for n in res[:, 11] if not np.isnan(n)]

    precs = np.array(precs)
    blink_rates = np.array(blink_rates)
    math_correct = np.array(math_correct)

    # Recently blink rates were changed from ratios to percentages on our reports. Therefore, we need to convert blink 
    # rates that are still expressed as ratios to percentages. (Note that this assumes all blink rates are above 1%)
    blink_rates[np.where(blink_rates <= 1)] *= 100

    # Calculate bonuses from each session that was input
    scores = []
    bonuses = []
    for i in range(len(subj_list)):
        subj = subj_list[i]
        sess = sess_list[i]

        # Load events for given subejct and session
        ev = BaseEventReader(filename='/data/eeg/scalp/ltp/ltpFR2/%s/session_%d/events.mat' % (subj, sess),
                             common_root='data').read()

        # Calculate performance from the target session
        sess_prec = calculate_prec(ev)
        sess_br = calculate_blink_rate(ev, pres_duration, return_percent=True)
        sess_mc = get_math_correct(subj, sess)

        # Calculate bonus based on percentile where the target session falls among performance on all past sessions
        prec_bonus = round(percentileofscore(precs, sess_prec) / 100. * 5, 2)
        blink_bonus = round((1 - percentileofscore(blink_rates, sess_br) / 100.) * 5, 2)
        math_bonus = round(percentileofscore(math_correct, sess_mc) / 100. * 5, 2)
        total_bonus = prec_bonus + blink_bonus + math_bonus

        # Add bonuses from session to running list
        scores.append((sess_prec, sess_br, sess_mc))
        bonuses.append((prec_bonus, blink_bonus, math_bonus, total_bonus))

    return scores, bonuses
'''
