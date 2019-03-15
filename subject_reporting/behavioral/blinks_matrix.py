import os
import numpy as np
from ptsa.data.readers import BaseEventReader


def make_blinks_matrix(exp, subj, sess, n_trials, list_length):
    """
    Creates a trials x items matrix indicating whether EOG artifacts were detected during each item presentation.
    The coding scheme is as follows:
    -1 - Unaligned event; blink detection not possible.
    0 - No artifacts detected.
    1 - Artifact detected on left eye channel.
    2 - Artifact detected on right eye channel.
    3 - Artifacts detected on both eye channels.

    :param exp: A string indicating the experiment name.
    :param subj: A string indicating the subject ID.
    :param sess: An integer indicating the session number.
    :param n_trials: An integer indicating the number of trials in the session.
    :param list_length: An integer indicating the number of items per trial in the session.
    :return: A trials x items array indicating whether EOG artifacts were detected during each item presentation.
    """
    evfile = '/protocols/ltp/subjects/%s/experiments/%s/sessions/%d/behavioral/current_processed/task_events.json' %\
             (subj, exp, sess)

    # If events do not exist yet, mark all entries as unaligned.
    if not os.path.exists(evfile):
        print('Warning: No events available for %s session %d!' % (subj, sess))
        blinks = np.zeros((n_trials, list_length), dtype='int16')
        blinks.fill(-1)

    # Otherwise, load event file for the session and create blinks matrix
    else:
        evs = BaseEventReader(filename=evfile, eliminate_events_with_no_eeg=False).read()
        evs = evs[evs.type == 'WORD']

        blinks = evs.eogArtifact
        blinks[evs.eegfile == ''] = -1  # Mark unaligned events with -1
        blinks = np.reshape(blinks, (n_trials, list_length))  # Reshape as trials x items

    return blinks
