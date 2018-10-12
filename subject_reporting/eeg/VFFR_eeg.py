import os
import mne
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from math import ceil
from subject_reporting.eeg.get_scalp_data import get_scalp_data

matplotlib.rc('font', size=18)  # default text sizes
matplotlib.rc('axes', titlesize=18)  # font size of the axes title
matplotlib.rc('axes', labelsize=18)  # font size of the x and y labels
matplotlib.rc('xtick', labelsize=18)  # font size of the x-axis tick labels
matplotlib.rc('ytick', labelsize=18)  # font size of the y-axis tick labels
matplotlib.rc('figure', titlesize=20)  # font size of the figure title


def eeg_VFFR(subj):
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
    samp_rate = 2048
    fz_chans = ['C12', 'C13', 'C20', 'C21', 'C25', 'C26']  # Fz channels
    cz_chans = ['A1', 'A2', 'B1', 'C1', 'D1', 'D15']  # Cz channels
    pz_chans = ['A5', 'A18', 'A19', 'A20', 'A31', 'A32']  # Pz channels
    tmin = -.3  # Start time of ERP in seconds
    tmax = 1.2  # End time of ERP in seconds

    n_samples = samp_rate * tmax - tmin
    erps = np.zeros((n_sess, 3, n_samples))
    erps.fill(np.nan)
    for sess in range(n_sess):

        # Get data from each word presentation event; skip session if no events or no EEG data
        eeg = get_scalp_data(subj, sess, exp, tmin, tmax)
        if eeg is None:
            continue

        # Apply common average reference (automatically excludes bad channels)
        eeg.set_eeg_reference(ref_channels='average', projection=False)

        # Baseline correct event data based on the 300 ms prior to word onset
        eeg.apply_baseline((None, 0))

        names = ['Fz', 'Cz', 'Pz']
        for i, erp_chs in enumerate((fz_chans, cz_chans, pz_chans)):

            try:
                # Calculate ERP
                evoked = eeg.average(picks=mne.pick_types(eeg.info, include=erp_chs))
                erps[sess, i, :] = evoked._data.mean(axis=0) * 1000000
            except Exception as e:
                print(e)
                continue

            # Plot ERP
            plt.axvline(x=0, ls='--', c='#011F5B')
            plt.axhline(y=0, ls='--', c='#990000')
            plt.xlim(evoked.times[0], evoked.times[-1])
            lim = ceil(np.abs(erps[sess, i, :]).max())  # Dynamically scale the range of the Y-axis
            plt.ylim(-lim, lim)
            plt.title('%s (%d$-$%d ms)' % (names[i], tmin * 1000, tmax * 1000))
            plt.plot(evoked.times, erps[sess, i, :], 'k', lw=1)
            plt.gcf().set_size_inches(7.5, 3.5)
            plt.tight_layout()

            # Make directory for ERP plots if it does not exist
            fig_dir = '/data/eeg/scalp/ltp/%s/%s/session_%d/figs/' % (exp, subj, sess)
            if not os.path.exists(fig_dir):
                os.mkdir(fig_dir)

            # Save ERP figure
            fig_name = '%s_erp.pdf' % names[i]
            plt.savefig(os.path.join(fig_dir, fig_name))
            plt.close()

        # Calculate cross-session average ERPs for the first 5 and last 5 sessions
        first5_avg = np.nanmean(erps[:5, :, :], axis=0)
        last5_avg = np.nanmean(erps[5:, :, :], axis=0)

        # Make directory for cross-session average ERP plots if it does not exist
        fig_dir = '/data/eeg/scalp/ltp/%s/%s/figs/' % (exp, subj)
        if not os.path.exists(fig_dir):
            os.mkdir(fig_dir)

        for i, roi in enumerate(names):
            # Plot ERP
            plt.axvline(x=0, ls='--', c='#011F5B')
            plt.axhline(y=0, ls='--', c='#990000')
            plt.xlim(evoked.times[0], evoked.times[-1])
            lim = ceil(np.abs(first5_avg[i, :]).max())  # Dynamically scale the range of the Y-axis
            plt.ylim(-lim, lim)
            plt.title('%s (%d$-$%d ms)' % (roi, tmin * 1000, tmax * 1000))
            plt.plot(evoked.times, first5_avg[i, :], 'k', lw=1)
            plt.plot(evoked.times, last5_avg[i, :], 'C1', lw=1)
            plt.legend(['Control Sessions', 'FFR Sessions'])
            plt.gcf().set_size_inches(7.5, 3.5)
            plt.tight_layout()
            fig_name = '%s_erp.pdf' % names[i]
            plt.savefig(os.path.join(fig_dir, fig_name))
            plt.close()


if __name__ == "__main__":
    s = input('Enter a subject ID: ')
    eeg_VFFR(s)
