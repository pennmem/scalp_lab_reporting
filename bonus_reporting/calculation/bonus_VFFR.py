from __future__ import print_function
import os
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
    # Get only word presentation and word recall events with eeg
    # in VFFR, subjects are instructed to not blink from when a word appears on screen 
    # and before they say the word aloud
    pres_and_rec_events = events[np.logical_and(np.logical_or(events['type'] == 'WORD', events['type'] == 'REC_WORD'),
                                                np.logical_not(events['eegfile'] == ''))]
    pres_events = pres_and_rec_events[pres_and_rec_events['type'] == 'WORD']
    # use indexes of pres events + 1 to get the first rec event in each trial
    # ignore the second rec event (if any) for now
    first_rec_events = pres_and_rec_events[np.where(pres_and_rec_events['type']=='WORD')[0] + 1]
    # some events from the line above will contain 'WORD' events if the trial contains no rec event, filter those out
    first_rec_events = first_rec_events[first_rec_events['type'] == 'REC_WORD']

    pres_and_rec_events = np.concatenate((pres_events, first_rec_events))

    # Count number of word presentations with artifactMS info
    total_pres = float(pres_and_rec_events.shape[0])
    # If there are no presentation events with artifactMS info, blink rate cannot be calculated
    if total_pres == 0:
        return np.nan

    # Count number of word presentations where eye movements were detected while the word was on the screen
    events_with_left_blink = np.logical_or(pres_and_rec_events['eogArtifact'] == 1, pres_and_rec_events['eogArtifact'] == 3).sum()
    events_with_right_blink = np.logical_or(pres_and_rec_events['eogArtifact'] == 2, pres_and_rec_events['eogArtifact'] == 3).sum()
    events_with_blink = np.sum(pres_and_rec_events['eogArtifact'] > 0)

    # Calculate blink rate as presentations with blinks / total presentations
    lbr = events_with_left_blink / total_pres if total_pres > 0 else np.nan
    rbr = events_with_right_blink / total_pres if total_pres > 0 else np.nan
    br = events_with_blink / total_pres if total_pres > 0 else np.nan

    if return_percent:
        return lbr * 100, rbr * 100, br * 100
    else:
        return lbr, rbr, br

def calculate_bad_trial_rate(events, return_percent=False):
    """
    Calculates a participant's bad trial rate on an events structure. Bad trials are defined to be trials in which
    the participant spoke too early or did not say the correct word. For fairness, speaking too early will only count
    against the participant if the word was annotated as too early AND the "too fast" message was displayed to the
    participant.
    """
    pres_events = events[events['type'] == 'WORD']
    bad_trials = pres_events[((pres_events['too_fast']) & (pres_events['too_fast_msg'])) | (pres_events['correct'] == 0)]
    btr = len(bad_trials) / float(len(pres_events))

    if return_percent:
        return btr * 100
    else:
        return btr

def calculate_bonus_VFFR(subj):
    """
    Calculates bonus payments for each of a participant's 24 sessions based on the following performance brackets:

    Performance:
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

    Performance scores and bonuses can only be calculated once the session has been annotated. Blink rates can only be
    calculated if the session has been successfully aligned and blink detection has been run. If not all presentation
    events have EEG data, the blink rate is calculated only over the events that do.

    :param subj: A string containing the subject ID of the participant for whom to calculate bonuses.
    :return: Returns two numpy arrays. The first is a session x score matrix, with prec in column 0 and blink rates in
    columns 1-3. The second is a session x bonus matrix, with recall bonus in column 0, blink bonus in column 1, and
    total bonus in column 2.
    """

    # Set experiment parameters and performance bracket boundaries
    n_sessions = 10
    brackets = dict(
        btr = [10, 20, 30, 40, 50],
        br=[10, 20, 30, 40, 50]
    )

    scores = np.zeros((n_sessions, 4))
    bonuses = np.zeros((n_sessions, 3))
    # Calculate scores and bonuses for each session
    for sess in range(n_sessions):
        print(subj, sess)
        # If session has exists and has been post-processed, calculate prec and blink rate, otherwise, set as nan
        event_file = '/protocols/ltp/subjects/%s/experiments/VFFR/sessions/%d/behavioral/current_processed/task_events.json' % (subj, sess)
        btr = np.nan
        lbr = np.nan
        rbr = np.nan
        br = np.nan
        try:
            # Calculate performance from the target session
            # Load events for given subject and session
            ev = BaseEventReader(filename=event_file, common_root='data', eliminate_nans=False, eliminate_events_with_no_eeg=False).read()
            lbr, rbr, br = calculate_blink_rate(ev, return_percent=True)
            btr = calculate_bad_trial_rate(ev, return_percent=True)
            del ev
        except Exception as e:
            # Exceptions here are caused by a nonexistent, empty, or otherwise unreadable event file.
            print(e)
            print('PTSA was unable to read event file %s... Leaving blink rate and trial rate as NaN!' % event_file)

        # Calculate bonuses based on performance brackets
        blink_bonus = 5 - np.searchsorted(brackets['br'], br, side='right') if not np.isnan(br) else np.nan
        trial_bonus = 5 - np.searchsorted(brackets['btr'], btr, side='right') if not np.isnan(btr) else np.nan
        total_bonus = blink_bonus + trial_bonus

        # Record scores and bonuses from session
        scores[sess] = [btr, round(lbr, 1), round(rbr, 1), round(br, 1)]
        bonuses[sess] = [trial_bonus, blink_bonus, total_bonus]

    return scores, bonuses
