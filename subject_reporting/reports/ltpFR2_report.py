import os
import json
import numpy as np
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
    tex_outfile = '/data/eeg/scalp/ltp/ltpFR2/%s/%s_report' % (subj, subj)
    tex_outfile = '/Users/jessepazdera/Desktop/testfigs/%s_report' % subj

    ###############
    #
    # Load data if not provided
    #
    ###############
    if stats is None:
        # Data may either be in beh_data_LTP###.json or beh_data_LTP###_incomplete.json
        data_file = os.path.join(stat_dir, 'stats_%s.json' % subj)
        if not os.path.exists(data_file):
            data_file = os.path.join(stat_dir, 'stats_%s_incomplete.json' % subj)
            if not os.path.exists(data_file):
                return dict()
        with open(data_file, 'r') as f:
            stats = json.load(f)

    ###############
    #
    # Extract information from stats dictionary
    #
    ###############
    sessions = np.array(stats['session'])
    num_good_trials = np.array(stats['num_good_trials'])
    p_rec = np.array(stats['p_rec'])
    spc = np.array(stats['spc'])
    pfr = np.array(stats['pfr'])
    crp = np.array(stats['crp'])
    crl = np.array(stats['crl'])
    pli_perlist = np.array(stats['pli_perlist'])
    xli_perlist = np.array(stats['xli_perlist'])
    rep_perlist = np.array(stats['rep_perlist'])

    ###############
    #
    # Initialize LaTeX report document
    #
    ###############
    geometry_options = dict(
        paperheight='6.5in',
        paperwidth='8in',
        margin='.5in'
    )
    doc = ltx.Document(page_numbers=False, geometry_options=geometry_options)

    ###############
    #
    # Create first tabular (PRec, PLIs, XLIs, Reps, NumTrials)
    #
    ###############
    header = ['Session', 'PRec', 'PLI', 'XLI', 'Rep', 'Good Trials']
    # Define the format of the LaTeX tabular -- one column for each item in the header
    fmt = ('X[r] ' * len(header)).strip()
    with doc.create(ltx.Center()) as centered:
        doc.append(ltx.LargeText('Subject Report: %s' % subj))
        doc.append(ltx.Command('par'))
        with centered.create(ltx.Tabu(fmt)) as data_table:
            data_table.add_row([''] * len(header))
            data_table.add_hline()
            data_table.add_row([''] * len(header))
            data_table.add_row(header, mapper=[ltx.utils.bold])
            data_table.add_row([''] * len(header))
            data_table.add_hline()
            data_table.add_row([''] * len(header))
            for i, sess in enumerate(sessions):
                data_table.add_row([sess, round(p_rec[i], 2), round(pli_perlist[i], 2), round(xli_perlist[i], 2), round(rep_perlist[i], 2), num_good_trials[i]])

    doc.generate_pdf(tex_outfile, compiler='pdflatex')

    return tex_outfile + '.pdf'


if __name__ == "__main__":
    s = input('Enter a subject ID: ')
    subject_report_ltpFR2(s)
