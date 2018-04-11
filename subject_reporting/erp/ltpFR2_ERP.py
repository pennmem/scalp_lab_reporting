import os
import mne
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from ptsa.data.readers import BaseEventReader
from math import ceil

matplotlib.rc('font', size=18)  # default text sizes
matplotlib.rc('axes', titlesize=18)  # fontsize of the axes title
matplotlib.rc('axes', labelsize=18)  # fontsize of the x and y labels
matplotlib.rc('xtick', labelsize=18)  # fontsize of the x-axis tick labels
matplotlib.rc('ytick', labelsize=18)  # fontsize of the y-axis tick labels
matplotlib.rc('figure', titlesize=20)  # fontsize of the figure title


def get_scalp_data(subj, sess, exp, tmin=0, tmax=1.6):
    evfile = '/protocols/ltp/subjects/%s/experiments/%s/sessions/%d/behavioral/current_processed/task_events.json' % (subj, exp, sess)
    if not os.path.exists(evfile):
        print('Warning: No events available for %s session %d!' % (subj, sess))
        return None
    evs = BaseEventReader(filename=evfile, eliminate_events_with_no_eeg=True).read()

    # Check number of EEG files aligned to session
    eegfiles = np.unique(evs.eegfile)
    eegfiles = [f for f in eegfiles if f != '']
    if len(eegfiles) == 0:
        print('Warning: %s session %d not aligned with any EEG files! No EEG data will be returned.' % (subj, sess))
        return None
    elif len(eegfiles) > 1:
        print('Warning: %s session %d has multiple EEG recordings! Multi-recording sessions are not currently supported. No EEG data will be returned.' % (subj, sess))
    eegfile = eegfiles[0]

    # Load EEG data
    if eegfile.endswith('.bdf'):
        raw = mne.io.read_raw_edf(eegfile, eog=['EXG1', 'EXG2', 'EXG3', 'EXG4'], misc=['EXG5', 'EXG6', 'EXG7', 'EXG8'], stim_channel='Status', montage='biosemi128', preload=False)
    elif eegfile.endswith('.mff') or eegfile.endswith('.raw'):
        raw = mne.io.read_raw_egi(eegfile, preload=False)
        raw.rename_channels({'E129': 'Cz'})
        raw.set_montage(mne.channels.read_montage('GSN-HydroCel-129'))
        raw.set_channel_types({'E8': 'eog', 'E25': 'eog', 'E126': 'eog', 'E127': 'eog', 'Cz': 'misc'})
    else:
        print('Warning: Unable to determine EEG recording type for %s session %d!' % (subj, sess))

    # Get event onsets and format them as MNE events
    mne_evs = np.zeros((len([t for t in evs.type if t == 'WORD']), 3), dtype=int)
    mne_evs[:, 0] = [o for i, o in enumerate(evs.eegoffset) if evs.type[i] == 'WORD']

    # Load epoch data from EEG recording
    ep = mne.Epochs(raw, mne_evs, event_id={'WORD': 0}, tmin=tmin, tmax=tmax, baseline=None, preload=True)

    # Drop unused channels and sync pulse channel
    ep.pick_types(eeg=True, eog=True)

    bad_chan_file = os.path.splitext(eegfile)[0] + '_bad_chan.txt'
    if os.path.exists(bad_chan_file):
        with open(bad_chan_file, 'r') as f:
            badchan = [s.strip() for s in f.readlines()]
    ep.info['bads'] = badchan

    return ep


def erp_ltpFR2(subj):
    """
    TBA

    :param subj:
    :return:
    """
    # Settings
    exp = 'ltpFR2'
    n_sess = 24  # Max number of sessions in experiment
    fz_chans = ['C21'] if int(subj[-3:]) > 330 else ['E11']  # Channel(s) to plot under Fz
    cz_chans = ['A1'] if int(subj[-3:]) > 330 else ['E55']  # Channel(s) to plot under Cz
    pz_chans = ['A19'] if int(subj[-3:]) > 330 else ['E62']  # Channel(s) to plot under Pz
    tmin = -.5  # Start time of ERP in seconds
    tmax = 1.6  # End time of ERP in seconds

    for sess in range(n_sess):
        # Get data from each word presentation event; skip session if no events or no EEG data
        eeg = get_scalp_data(subj, sess, exp, tmin, tmax)
        if eeg is None:
            continue
        # Apply common average reference (automatically excludes bad channels)
        eeg.set_eeg_reference(ref_channels='average', projection=False)
        # Baseline correct event data based on the 500 ms prior to word onset
        eeg.apply_baseline((None, 0))

        names = ['Fz', 'Cz', 'Pz']
        for i, erp_chs in enumerate((fz_chans, cz_chans, pz_chans)):
            try:
                # Calculate ERP
                erp = eeg.average(picks=mne.pick_types(eeg.info, include=erp_chs))
            except:
                # Failure here is likely due to channel name(s) not being recognized
                continue

            # Plot ERP
            lim = ceil(np.abs(erp.data).max() * 1000000)  # Dynamically scale the range of the Y-axis
            fig = erp.plot(ylim={'eeg': (-lim, lim)}, hline=[0], selectable=False)
            plt.title('%s (%d -- %d ms)' % (names[i], tmin * 1000, tmax * 1000))
            plt.axvline(x=0, ls='--')  # Mark word onset
            # plt.axvline(x=1600, ls='--')  # Mark word offset

            # Save ERP to <ID>_<SESS>_<CHAN>_erp.pdf; add extra number at end if session has multiple recordings
            fig_name = '%s_erp.pdf' % names[i]
            # Make directory for figures/ERP plots if it does not exist
            fig_dir = '/data/eeg/scalp/ltp/%s/%s/session_%d/figs/' % (exp, subj, sess)
            if not os.path.exists(fig_dir):
                os.mkdir(fig_dir)
            fig.savefig(os.path.join(fig_dir, fig_name))
            plt.close(fig)

            """
            # EXAMPLE ICA CODE
            fz = pres_eeg.average(picks=mne.pick_types(pres_eeg.info, include=fz_chans))
            ica_fname = '/home1/jpazdera/ICA/LTP342_10/reref-ica.fif'
            ica = mne.preprocessing.read_ica(ica_fname)
            ica.apply(eeg)
            fz_ica = pres_eeg.average(picks=mne.pick_types(pres_eeg.info, include=fz_chans))
            fz_ica.rename_channels({chan: (chan + '_ica') for chan in fz_ica.info['ch_names']})
            fz.add_channels([fz_ica])

            # fz now has ERPs for pre- and post-ica
            """


if __name__ == "__main__":
    erp_ltpFR2('LTP368')
