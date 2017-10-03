import os
import mne
import numpy as np
import matplotlib.pyplot as plt
from ptsa.data.readers import BaseEventReader
from math import ceil


def erp_ltpFR2(subj):
    exp_dir = '/data/eeg/scalp/ltp/ltpFR2/'
    n_sess = 24

    for sess in range(n_sess):
        # Load word presentation events from target session
        evfile = os.path.join(exp_dir, subj, sess, 'events.json')
        ev = BaseEventReader(filename=evfile, normalize_eeg_path=False, eliminate_events_with_no_eeg=True).read()
        ev = ev[ev.type == 'WORD']

        # Get list of all unique EEG files that have been aligned to the events
        eegfiles = np.unique(ev.eegfile)
        for i, fname in enumerate(eegfiles):

            # Add full path to an EEG file, load it, and re-reference to the common average
            eeg = mne.io.read_raw_fif(os.path.join(exp_dir, subj, sess, 'eeg', fname), preload=True)
            eeg.apply_proj()

            # Get offsets for events from the current EEG file
            offsets = ev.offsets[ev.eegfile == fname]

            # Use offsets to get data from events
            mne_evs = np.array([[o, 0, 1] for o in offsets])
            eeg = mne.Epochs(eeg, mne_evs, event_id=1, tmin=-.5, tmax=2.1, baseline=(None, 0))


if __name__ == "__main__":
    # ERP timing settings
    tmin = -.5
    tmax = 2.4

    # Load behavioral data -> eeg offsets
    ev = BaseEventReader(filename='/Users/jpazdera/rhino_mount/data/eeg/scalp/ltp/ltpFR2/LTP342/session_10/events.mat', normalize_eeg_path=False, eliminate_events_with_no_eeg=True).read()
    ev = ev[ev.type == 'WORD']
    offsets = ev.eegoffset
    mne_evs = np.array([[int(o/2), 0, 1] for o in offsets])

    # Load EEG data
    fname = '/Users/jpazdera/rhino_mount/home1/jpazdera/ICA/LTP342_10/raw.fif'
    eeg = mne.io.read_raw_fif(fname, preload=True)
    eeg.apply_proj()

    # Create ERPs for Fz, Cz, and Pz electrodes
    pres_eeg = mne.Epochs(eeg, mne_evs, event_id=1, tmin=tmin, tmax=tmax, baseline=(None, 0), preload=True)
    fz = pres_eeg.average(picks=mne.pick_types(pres_eeg.info, include=['C21']))
    cz = pres_eeg.average(picks=mne.pick_types(pres_eeg.info, include=['A1']))
    pz = pres_eeg.average(picks=mne.pick_types(pres_eeg.info, include=['A19']))

    # Plot ERP for each of the three electrodes
    names = ['Fz', 'Cz', 'Pz']
    for i, erp in enumerate((fz, cz, pz)):
        lim = ceil(np.abs(erp.data).max() * 1000000)  # Dynamically adjust the Y-axis
        fig = erp.plot(ylim={'eeg': (-lim, lim)}, hline=[0], selectable=False)
        plt.title('%s (%d -- %d ms)' % (names[i], tmin * 1000, tmax * 1000))
        plt.axvline(x=0, ls='--')
        plt.axvline(x=1600, ls='--')
        fig.savefig('%s_erp.pdf' % names[i])

    """
    # ICA CODE
    ica_fname = '/home1/jpazdera/ICA/LTP342_10/reref-ica.fif'
    ica = mne.preprocessing.read_ica(ica_fname)
    ica.apply(eeg)
    fz_ica = pres_eeg.average(picks=mne.pick_types(pres_eeg.info, include=['C21']))
    cz_ica = pres_eeg.average(picks=mne.pick_types(pres_eeg.info, include=['A1']))
    pz_ica = pres_eeg.average(picks=mne.pick_types(pres_eeg.info, include=['A19']))
    fz_ica.rename_channels({chan: (chan + '_ica') for chan in fz_ica.info['ch_names']})
    fz.add_channels([fz_ica])
    cz_ica.rename_channels({chan: (chan + '_ica') for chan in cz_ica.info['ch_names']})
    cz.add_channels([cz_ica])
    pz_ica.rename_channels({chan: (chan + '_ica') for chan in pz_ica.info['ch_names']})
    pz.add_channels([pz_ica])
    """
