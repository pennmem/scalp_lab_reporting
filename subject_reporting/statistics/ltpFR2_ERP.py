import os
import mne
import numpy as np
from ptsa.data.readers import BaseEventReader, EEGReader


def erp_ltpFR2(subj, stats=None):
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





import os
import mne
import numpy as np
import matplotlib.pyplot as plt
from ptsa.data.readers import BaseEventReader
from math import ceil

ev = BaseEventReader(filename='/data/eeg/scalp/ltp/ltpFR2/LTP342/session_10/events.mat', normalize_eeg_path=False, eliminate_events_with_no_eeg=True).read()
ev = ev[ev.type == 'WORD']
fname = '/Users/jessepazdera/rhino_mount/home1/jpazdera/ICA/LTP342_10/raw.fif'
eeg = mne.io.read_raw_fif(fname, preload=True)
eeg.apply_proj()
offsets = ev.eegoffset
mne_evs = np.array([[int(o/2), 0, 1] for o in offsets])
eeg = mne.Epochs(eeg, mne_evs, event_id=1, tmin=-.5, tmax=2.1, baseline=(None, 0), preload=True)
fz = eeg.average(picks=mne.pick_types(eeg.info, include=['C21']))
cz = eeg.average(picks=mne.pick_types(eeg.info, include=['A1']))
pz = eeg.average(picks=mne.pick_types(eeg.info, include=['A19']))

for erp in (fz, cz, pz):
    erp.plot(show=False)
    plt.axvline(x=0)
    plt.axvline(x=1600)
    plt.axhline(y=0)
    lim = max(3, ceil(1000000 * np.abs(erp.data).max()))
    plt.ylim((-lim, lim))
    plt.show()
