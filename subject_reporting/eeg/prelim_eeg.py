import os
import mne
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from math import ceil
from subject_reporting.eeg.get_scalp_data import get_scalp_data

matplotlib.rc('font', size=18)  # default text sizes
matplotlib.rc('axes', titlesize=18)  # fontsize of the axes title
matplotlib.rc('axes', labelsize=18)  # fontsize of the x and y labels
matplotlib.rc('xtick', labelsize=18)  # fontsize of the x-axis tick labels
matplotlib.rc('ytick', labelsize=18)  # fontsize of the y-axis tick labels
matplotlib.rc('figure', titlesize=20)  # fontsize of the figure title


def eeg_prelim(subj):
    """
    TBA

    :param subj: The participant for whom ERPs will be plotted.
    :return: None
    """
    # Settings
    exp = 'prelim'
    n_sess = 1  # Max number of sessions in experiment
    fz_chans = ['C12', 'C13', 'C20', 'C21', 'C25', 'C26']
    cz_chans = ['A1', 'A2', 'B1', 'C1', 'D1', 'D15']
    pz_chans = ['A5', 'A18', 'A19', 'A20', 'A31', 'A32']
    tmin = -.5  # Start time of ERP in seconds
    tmax = 2.1  # End time of ERP in seconds

    for sess in range(n_sess):

        # Make directory for ERP plots if it does not exist
        fig_dir = '/data/eeg/scalp/ltp/%s/%s/session_%d/figs/' % (exp, subj, sess)
        if not os.path.exists(fig_dir):
            os.mkdir(fig_dir)

        # Get data from each word presentation event; skip session if no events or no EEG data
        eeg = get_scalp_data(subj, sess, exp, tmin, tmax)
        if eeg is None:
            continue

        # Apply common average reference (automatically excludes bad channels)
        eeg.set_eeg_reference(ref_channels='average', projection=False)

        # Baseline correct event data based on the 500 ms prior to word onset
        eeg.apply_baseline((-.25, 0))

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
    eeg_prelim(s)
