from __future__ import print_function
import os
import csv
import numpy as np
from glob import glob
from ptsa.data.readers import BaseEventReader


def calculate_blink_rate(events, return_percent=False):
    """
    Calculates a participant's blink rate based on an events structure. This requires alignment and artifact detection
    to have already been run on the session's EEG data. The blink rate is defined as the fraction of presentation events
    during which the participant blinked or showed other EOG artifacts while the presented item was on the screen. For
    sessions where some presentation events lack EEG data, only the presentation events with data are counted.

    :param events: An events structure
    :param pres_duration: The number of milliseconds for which each item was presented on the screen (1600 for ltpFR2)
    :param return_percent: If true, returns the blink rate as a percentage. If false, returns the blink rate as a ratio.
    :return: The participant's left-eye, right-eye, and combined blink rates, or np.nan if no presentation events with
    EEG data are available.
    """
    # Get only word presentation events with eeg
    pres_events = events[np.logical_and(events['type'] == 'WORD', np.logical_not(events['eegfile'] == ''))]
    # Count number of word presentations with artifactMS info
    total_pres = float(pres_events.shape[0])
    # If there are no presentation events with artifactMS info, blink rate cannot be calculated
    if total_pres == 0:
        return np.nan

    # Count number of word presentations where eye movements were detected while the word was on the screen
    pres_with_left_blink = np.logical_or(pres_events['eogArtifact'] == 1, pres_events['eogArtifact'] == 3).sum()
    pres_with_right_blink = np.logical_or(pres_events['eogArtifact'] == 2, pres_events['eogArtifact'] == 3).sum()
    pres_with_blink = np.sum(pres_events['eogArtifact'] > 0)

    # Calculate blink rate as presentations with blinks / total presentations
    lbr = pres_with_left_blink / total_pres if total_pres > 0 else np.nan
    rbr = pres_with_right_blink / total_pres if total_pres > 0 else np.nan
    br = pres_with_blink / total_pres if total_pres > 0 else np.nan

    if return_percent:
        return lbr * 100, rbr * 100, br * 100
    else:
        return lbr, rbr, br

def calculate_bonus_delayrepfr(subj):
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

    Recall scores and bonuses can only be calculated once the session has been annotated. Blink rates can only be
    calculated if the session has been successfully aligned and blink detection has been run. If not all presentation
    events have EEG data, the blink rate is calculated only over the events that do.

    :param subj: A string containing the subject ID of the participant for whom to calculate bonuses.
    :return: Returns two numpy arrays. The first is a session x score matrix, with prec in column 0, blink rates in
    columns 1-3, and math score in column 4. The second is a session x bonus matrix, with recall bonus in column 0,
    blink bonus in column 1, math bonus in column 2, and total bonus in column 3.
    """

    # Set experiment parameters and performance bracket boundaries
    n_sessions = 24
    brackets = dict(
        prec=[20, 30, 40, 50, 70],
        br=[10, 20, 30, 40, 50],
    )

    scores = np.zeros((24, 4))
    bonuses = np.zeros((24, 3))
    # Calculate scores and bonuses for each session
    for sess in range(n_sessions):
        print(subj, sess)
        # If session has exists and has been post-processed, calculate prec and blink rate, otherwise, set as nan
        event_file = '/protocols/ltp/subjects/%s/experiments/ltpDelayRepFRReadOnly/sessions/%d/behavioral/current_processed/task_events.json' % (subj, sess)
        prec = np.nan
        lbr = np.nan
        rbr = np.nan
        br = np.nan
        try:
            # Calculate performance from the target session
            sess_dir = '/data/eeg/scalp/ltp/ltpDelayRepFRReadOnly/%s/session_%d/' % (subj, sess)
            sess_precs = []
            lsts = glob(os.path.join(sess_dir, '*.lst'))
            for lst in lsts:
                par = os.path.splitext(lst)[0] + '.par'
                with open(lst, 'r') as f:
                    # filter out repeats, if present in lst
                    pres = set(w.strip() for w in f.readlines())
                if os.path.exists(par):
                    with open(par, 'r') as f:
                        rec = [w.split('\t')[2].strip() for w in f.readlines()]
                        recalled = [(w in rec) for w in pres]
                        sess_precs.append(np.mean(recalled))
                else:
                    sess_precs.append(np.nan)
            prec = np.nanmean(sess_precs) * 100

            # Load events for given subject and session
            ev = BaseEventReader(filename=event_file, common_root='data', eliminate_nans=False, eliminate_events_with_no_eeg=False).read()
            lbr, rbr, br = calculate_blink_rate(ev, return_percent=True)
            del ev
        except Exception as e:
            # Exceptions here are caused by a nonexistent, empty, or otherwise unreadable event file.
            print(e)
            print('PTSA was unable to read event file %s... Leaving blink rate and recall probability as NaN!' % event_file)

        # Calculate bonuses based on performance brackets
        prec_bonus = np.searchsorted(brackets['prec'], prec, side='right') if not np.isnan(prec) else np.nan
        blink_bonus = 5 - np.searchsorted(brackets['br'], br, side='right') if not np.isnan(br) else np.nan
        total_bonus = prec_bonus + blink_bonus

        # Record scores and bonuses from session
#        scores[sess] = [prec, round(lbr, 1), round(rbr, 1), round(br, 1), perf_bonus]
        scores[sess] = [prec, round(lbr, 1), round(rbr, 1), round(br, 1)]
        bonuses[sess] = [prec_bonus, blink_bonus, total_bonus]

    return scores, bonuses
