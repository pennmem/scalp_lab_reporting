import os
import mne
import numpy as np
from ptsa.data.readers import BaseEventReader


def get_scalp_data(subj, sess, exp, tmin=0, tmax=1.6):
    """
    Loads EEG data from the specified session, and constructs an MNE Epochs object containing the data from each
    word presentation event.

    :param subj: The subject who completed the session for which data will be loaded.
    :param sess: The session number of the session for which data will be loaded.
    :param exp: The experiment in which the session took place.
    :param tmin: The start time in seconds of the data to be loaded, relative to the onset of each event.
    :param tmax: The end time in seconds of the data to be loaded, relative to the onset of each event.
    :return: An MNE Epochs object containing data for each word presentation in the specified session.
    """
    # Load event file for the session
    evfile = '/protocols/ltp/subjects/%s/experiments/%s/sessions/%d/behavioral/current_processed/task_events.json' % (
    subj, exp, sess)
    if not os.path.exists(evfile):
        print('Warning: No events available for %s session %d!' % (subj, sess))
        return None
    evs = BaseEventReader(filename=evfile, eliminate_events_with_no_eeg=True).read()
    # Filter out all non-presentation events
    evs = evs[evs.type == 'WORD']

    # Check number of EEG files aligned to session, as well as the number of word presentations in that file
    eegfiles, pres_counts = np.unique(evs.eegfile, return_counts=True)
    eegfiles = [f for f in eegfiles if f != '']

    # If the session has no EEG recording, do not attempt to generate ERPs
    if len(eegfiles) == 0:
        print('Warning: %s session %d not aligned with any EEG files! No ERPs can be generated.' % (subj, sess))
        return None
    # If 1 recording, use it; if multiple recordings, use the one that encompasses the most word presentation events
    else:
        eegfile = eegfiles[np.argmax(pres_counts)]
        if len(eegfiles) > 1:
            print('Warning: %s session %d has multiple EEG recordings! Using the recording with the most events...' % (
            subj, sess))

    # Load EEG data
    if eegfile.endswith('.bdf'):
        raw = mne.io.read_raw_edf(eegfile, eog=['EXG1', 'EXG2', 'EXG3', 'EXG4'], misc=['EXG5', 'EXG6', 'EXG7', 'EXG8'],
                                  stim_channel='Status', montage='biosemi128', preload=False)
    elif eegfile.endswith('.mff') or eegfile.endswith('.raw'):
        raw = mne.io.read_raw_egi(eegfile, preload=False)
        raw.rename_channels({'E129': 'Cz'})
        raw.set_montage(mne.channels.read_montage('GSN-HydroCel-129'))
        raw.set_channel_types({'E8': 'eog', 'E25': 'eog', 'E126': 'eog', 'E127': 'eog', 'Cz': 'misc'})
    else:
        print('Warning: Unable to determine EEG recording type for %s session %d!' % (subj, sess))

    # Get event onsets and format them as MNE events
    mne_evs = np.zeros((len(evs), 3), dtype=int)
    mne_evs[:, 0] = evs.eegoffset

    # Load epoch data from EEG recording
    ep = mne.Epochs(raw, mne_evs, event_id={'WORD': 0}, tmin=tmin, tmax=tmax, baseline=None, preload=True)

    # Drop unused channels and sync pulse channel
    ep.pick_types(eeg=True, eog=False, misc=False)

    # Add bad channel info to the MNE object
    bad_chan_file = os.path.splitext(eegfile)[0] + '_bad_chan.txt'
    if os.path.exists(bad_chan_file):
        with open(bad_chan_file, 'r') as f:
            badchan = [s.strip() for s in f.readlines()]
        ep.info['bads'] = badchan

    return ep