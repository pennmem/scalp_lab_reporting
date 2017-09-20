import os
import pylatex as ltx


def subject_report_ltpFR2(subj, stats=None):
    """
    TBA

    :param subj:
    :param stats:
    :return:
    """

    ###############
    #
    # Define parameters of experiment
    #
    ###############
    stat_dir = '/data/eeg/scalp/ltp/ltpFR2/behavioral/stats/'
    out_dir = '/data/eeg/scalp/ltp/ltpFR2/report/'

    outfile = os.path.join(out_dir, '%s_report.pdf' % subj)
    return outfile


if __name__ == "__main__":
    s = input('Enter a subject ID: ')
    subject_report_ltpFR2(s)
