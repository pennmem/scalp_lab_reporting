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


def erp_ltpFR2(subj):
    """
    TBA

    :param subj:
    :return:
    """
    # Settings
    db_dir = '/protocols/ltp/subjects/%s/experiments/ltpFR2/sessions/' % subj
    out_dir = '/data/eeg/scalp/ltp/ltpFR2/'
    n_sess = 24  # Max number of sessions in experiment
    fz_chans = ['C21']  # Channel(s) to plot under Fz
    cz_chans = ['A1']  # Channel(s) to plot under Cz
    pz_chans = ['A19']  # Channel(s) to plot under Pz
    tmin = -.5  # Start time of ERP in seconds
    tmax = 2.1  # End time of ERP in seconds

    for sess in range(n_sess):
        # Make directory for figures/ERP plots if it does not exist
        fig_dir = os.path.join(out_dir, subj, 'session_' + str(sess), 'figs')
        if not os.path.exists(fig_dir):
            os.mkdir(fig_dir)

        evfile = os.path.join(db_dir, str(sess), 'behavioral', 'current_processed', 'task_events.json')
        if not os.path.exists(evfile):  # Skip session if events have not been processed
            continue
        # Load word presentation events from target session
        ev = BaseEventReader(filename=evfile, eliminate_events_with_no_eeg=True).read()
        ev = ev[ev.type == 'WORD']

        # Get list of all unique EEG files that have been aligned to the events from the target session
        eegfiles = [f for f in np.unique(ev.eegfile) if f != '']
        for i, fname in enumerate(eegfiles):
            eegfile = os.path.join(db_dir, str(sess), 'ephys', 'current_processed', os.path.basename(fname) + '.fif')
            # Skip EEG file if it cannot be found (only happens if EEG file was moved/deleted after alignment)
            if not os.path.exists(eegfile):
                continue
            # Add full path to an EEG file, load it, and re-reference to the common average
            eeg = mne.io.read_raw_fif(eegfile, preload=True)
            eeg.apply_proj()

            # Get offsets for events from the current EEG file
            offsets = ev.eegoffset[ev.eegfile == fname]

            # Use offsets to get data from presentation events (baseline corrected using timing tmin -> 0)
            mne_evs = np.array([[o, 0, 1] for o in offsets], dtype=int)
            pres_eeg = mne.Epochs(eeg, mne_evs, event_id=1, tmin=tmin, tmax=tmax, baseline=(None, 0), preload=True)

            # Save ERP plots for Fz, Cz, and Pz electrodes
            names = ['Fz', 'Cz', 'Pz']
            for j, erp_chs in enumerate((fz_chans, cz_chans, pz_chans)):
                try:
                    # Calculate ERP
                    erp = pres_eeg.average(picks=mne.pick_types(pres_eeg.info, include=erp_chs))
                except:
                    # Failure here is likely due to channel name(s) not being recognized
                    continue

                # Plot ERP
                lim = ceil(np.abs(erp.data).max() * 1000000)  # Dynamically scale the range of the Y-axis
                fig = erp.plot(ylim={'eeg': (-lim, lim)}, hline=[0], selectable=False)
                plt.title('%s (%d -- %d ms)' % (names[j], tmin * 1000, tmax * 1000))
                plt.axvline(x=0, ls='--')  # Mark word onset
                plt.axvline(x=1600, ls='--')  # Mark word offset

                # Save ERP to <ID>_<SESS>_<CHAN>_erp.pdf; add extra number at end if session has multiple recordings
                fig_name = '%s_erp_%d.pdf' % (names[j], i) if len(eegfiles) > 1 else '%s_erp.pdf' % names[j]
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
    erp_ltpFR2('LTP367')

    """
    tmin = -.5  # Start time of ERP in seconds
    tmax = 2.1  # End time of ERP in seconds

    # Load behavioral data -> eeg offsets
    evfile = '/data/eeg/scalp/ltp/ltpFR2/LTP342/session_10/events.mat'
    ev = BaseEventReader(filename=evfile, normalize_eeg_path=False, eliminate_events_with_no_eeg=True).read()
    offsets = ev.eegoffset
    mne_evs = np.array([[int(o/2), 0, 1] for o in offsets])

    # Load EEG data
    fname = '/Users/jessepazdera/rhino_mount/home1/jpazdera/ICA/LTP342_10/raw.fif'
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
        fig.savefig('/Users/jessepazdera/rhino_mount/home1/jpazdera/jupyter/%s_erp.pdf' % names[i])
        plt.close(fig)
    """