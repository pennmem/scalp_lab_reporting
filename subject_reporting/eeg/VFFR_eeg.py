import os
import mne
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from ptsa.data.readers import BaseEventReader
from math import ceil

matplotlib.rc('font', size=18)  # default text sizes
matplotlib.rc('axes', titlesize=18)  # font size of the axes title
matplotlib.rc('axes', labelsize=18)  # font size of the x and y labels
matplotlib.rc('xtick', labelsize=18)  # font size of the x-axis tick labels
matplotlib.rc('ytick', labelsize=18)  # font size of the y-axis tick labels
matplotlib.rc('figure', titlesize=20)  # font size of the figure title


def get_VFFR_data(subj, sess, tmin=0, tmax=1.6):
    """
    Loads EEG data from the specified VFFR sessions, and constructs an MNE Epochs object containing the data from each
    word presentation event.

    :param subj: The subject who completed the session for which data will be loaded.
    :param sess: The session number of the session for which data will be loaded.
    :param tmin: The start time in seconds of the data to be loaded, relative to the onset of each event.
    :param tmax: The end time in seconds of the data to be loaded, relative to the onset of each event.
    :return: An MNE Epochs object containing data for each word presentation in the specified session.
    """
    # Load event file for the session
    evfile = '/protocols/ltp/subjects/%s/experiments/VFFR/sessions/%d/behavioral/current_processed/task_events.json' % (subj, sess)
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
            print('Warning: %s session %d has multiple EEG recordings! Using the recording with the most events...' % (subj, sess))

    # Load EEG data
    raw = mne.io.read_raw_edf(eegfile, eog=['EXG1', 'EXG2', 'EXG3', 'EXG4'], misc=['EXG5', 'EXG6', 'EXG7', 'EXG8'], stim_channel='Status', montage='biosemi128', preload=False)

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


def eeg_ltpFR2(subj):
    """
    Plots ERPs for word presentation events during each of a subject's sessions at three regions of interest
    (Fz, Cz, Pz). In generating ERPs, data is common average re-referenced with bad channels excluded. Then the data
    is baseline corrected and averaged across trials. Data is plotted in microvolts, and is displayed for 300 ms before
    word onset to 1200 ms post-onset (the minimum duration for which a word can be displayed).

    :param subj: The participant for whom ERPs will be plotted.
    :return: None
    """
    # Settings
    exp = 'VFFR'
    n_sess = 10  # Max number of sessions in experiment
    fz_chans = ['C12', 'C13', 'C20', 'C21', 'C25', 'C26']  # Channel(s) to plot under Fz
    cz_chans = ['A1', 'A2', 'B1', 'C1', 'D1', 'D15']  # Channel(s) to plot under Cz
    pz_chans = ['A5', 'A18', 'A19', 'A20', 'A31', 'A32']  # Channel(s) to plot under Pz
    tmin = -.3  # Start time of ERP in seconds
    tmax = 1.2  # End time of ERP in seconds

    for sess in range(n_sess):

        # Make directory for ERP plots if it does not exist
        fig_dir = '/data/eeg/scalp/ltp/%s/%s/session_%d/figs/' % (exp, subj, sess)
        if not os.path.exists(fig_dir):
            os.mkdir(fig_dir)

        # Get data from each word presentation event; skip session if no events or no EEG data
        eeg = get_VFFR_data(subj, sess, tmin, tmax)
        if eeg is None:
            continue

        # Apply common average reference (automatically excludes bad channels)
        eeg.set_eeg_reference(ref_channels='average', projection=False)

        # Baseline correct event data based on the 300 ms prior to word onset
        eeg.apply_baseline((None, 0))

        names = ['Fz', 'Cz', 'Pz']
        erps = np.zeros((len(names), len(eeg.times)))
        for i, erp_chs in enumerate((fz_chans, cz_chans, pz_chans)):

            try:
                # Calculate ERP
                evoked = eeg.average(picks=mne.pick_types(eeg.info, include=erp_chs))
                erps[i, :] = evoked._data.mean(axis=0) * 1000000
            except Exception as e:
                print(e)
                continue

            # Plot ERP
            plt.axvline(x=0, ls='--', c='#011F5B')
            plt.axhline(y=0, ls='--', c='#990000')
            plt.xlim(evoked.times[0], evoked.times[-1])
            lim = ceil(np.abs(erps[i]).max())  # Dynamically scale the range of the Y-axis
            plt.ylim(-lim, lim)
            plt.title('%s (%d$-$%d ms)' % (names[i], tmin * 1000, tmax * 1000))
            plt.plot(evoked.times, erps[i], 'k', lw=1)
            plt.gcf().set_size_inches(7.5, 3.5)
            plt.tight_layout()

            # Save ERP figure
            fig_name = '%s_erp.pdf' % names[i]
            plt.savefig(os.path.join(fig_dir, fig_name))
            plt.close()


if __name__ == "__main__":
    s = input('Enter a subject ID: ')
    eeg_ltpFR2(s)
