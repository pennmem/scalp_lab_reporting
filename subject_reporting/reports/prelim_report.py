import os
import numpy as np
import pylatex as ltx
from .load_stats import load_stats


def subject_report_prelim(subj):
    """
    Create a subject report for the specified prelim participant.

    :param subj: The subject for whom a report will be generated.
    :return: The filepath of the PDF report.
    """
    ###############
    #
    # Define parameters of experiment
    #
    ###############
    exp = 'prelim'
    subj_dir = '/data/eeg/scalp/ltp/%s/%s/' % (exp, subj)
    tex_outfile = '/data/eeg/scalp/ltp/%s/%s/%s_report' % (exp, subj, subj)

    ###############
    #
    # Load performance stats from file
    #
    ###############

    stats = load_stats(exp, subj)
    if not stats:
        return None
    sessions = np.array(stats['session'])
    num_good_trials = np.array(stats['num_good_trials'])
    p_rec = np.array(stats['p_rec'])
    pli_perlist = np.array(stats['pli_perlist'])
    xli_perlist = np.array(stats['xli_perlist'])
    rep_perlist = np.array(stats['rep_perlist'])
    blink_rate = np.array(stats['blink_rate']) * 100

    ###############
    #
    # Initialize LaTeX report document
    #
    ###############
    geometry_options = dict(
        paperheight='11in',
        paperwidth='8.5in',
        margin='.5in'
    )
    doc = ltx.Document(page_numbers=False, geometry_options=geometry_options)
    doc.preamble.append(ltx.Package('graphicx'))  # Load graphicx package so that we can use \includegraphics

    with doc.create(ltx.Center()) as centered:
        doc.append(ltx.LargeText(ltx.Command('underline', arguments='Subject Report: %s' % subj)))
        doc.append(ltx.Command('break'))
        doc.append(ltx.Command('break'))
        doc.append(ltx.Command('break'))

        ###############
        #
        # Create first table (PRec, PLIs, XLIs, Reps, Trials)
        #
        ###############
        header = ['Sess', 'PRec', 'PLI', 'ELI', 'Rep', 'Blink Rate', 'Trials']
        fmt = '|c' * len(header) + '|'
        with centered.create(ltx.Tabu(fmt)) as data_table:
            data_table.add_hline()
            data_table.add_row([''] * len(header))
            data_table.add_row(header, mapper=[ltx.utils.bold])
            data_table.add_row([''] * len(header))
            data_table.add_hline()
            data_table.add_row([''] * len(header))
            for i, sess in enumerate(sessions):
                blink_rate_string = str(round(blink_rate[i, 0], 2)) + '% / ' + str(round(blink_rate[i, 1], 2)) + '% / '\
                                    + str(round(blink_rate[i, 2], 2)) + '%'
                data_table.add_row([sess, round(p_rec[i], 2), round(pli_perlist[i], 2), round(xli_perlist[i], 2),
                                    round(rep_perlist[i], 2), blink_rate_string, num_good_trials[i]])
            data_table.add_row([''] * len(header))
            data_table.add_hline()

        ###############
        #
        # Create second table (SPC, PFR, CRP plots)
        #
        ###############
        doc.append(ltx.Command('break'))
        doc.append(ltx.Command('break'))
        doc.append(ltx.Command('break'))
        doc.append(ltx.Command('break'))
        doc.append(ltx.Command('break'))
        doc.append(ltx.MediumText('Dynamics of Recall'))
        header = ['Session', 'SPC', 'PFR', 'CRP']
        fmt = 'c' * len(header)
        with centered.create(ltx.LongTabu(fmt)) as data_table:
            data_table.add_hline()
            data_table.add_row([''] * len(header))
            data_table.add_row(header, mapper=[ltx.utils.bold])
            data_table.add_row([''] * len(header))
            data_table.add_hline()
            data_table.add_row([''] * len(header))

            # Average plot (Prelim session only uses this plot)
            sesstext = ltx.Command('raisebox', arguments=[ltx.NoEscape('0.105\\textwidth'), 'Avg'])
            spc_path = os.path.join(subj_dir, 'figs', 'spc.pdf')
            pfr_path = os.path.join(subj_dir, 'figs', 'pfr.pdf')
            crp_path = os.path.join(subj_dir, 'figs', 'crp.pdf')
            spcfig = pfrfig = crpfig = ''
            if os.path.exists(spc_path):
                spcfig = ltx.Command('includegraphics', options=ltx.NoEscape('width=0.27\\textwidth'),
                                     arguments=ltx.NoEscape(spc_path))
            if os.path.exists(pfr_path):
                pfrfig = ltx.Command('includegraphics', options=ltx.NoEscape('width=0.27\\textwidth'),
                                     arguments=ltx.NoEscape(pfr_path))
            if os.path.exists(crp_path):
                crpfig = ltx.Command('includegraphics', options=ltx.NoEscape('width=0.27\\textwidth'),
                                     arguments=ltx.NoEscape(crp_path))
            data_table.add_row([sesstext, spcfig, pfrfig, crpfig])

        ###############
        #
        # Create third table (ERP plots)
        #
        ###############
        doc.append(ltx.Command('break'))
        doc.append(ltx.Command('break'))
        doc.append(ltx.Command('break'))
        doc.append(ltx.Command('break'))
        doc.append(ltx.Command('break'))
        doc.append(ltx.MediumText('Event-Related Potentials'))
        header = ['Session', 'Fz', 'Cz', 'Pz']
        fmt = 'c' * len(header)
        with centered.create(ltx.LongTabu(fmt)) as data_table:
            data_table.add_hline()
            data_table.add_row([''] * len(header))
            data_table.add_row(header, mapper=[ltx.utils.bold])
            data_table.add_row([''] * len(header))
            data_table.add_hline()
            data_table.add_row([''] * len(header))
            for i, sess in enumerate(sessions):
                sesstext = ltx.Command('raisebox', arguments=[ltx.NoEscape('0.067\\textwidth'), sess])
                fz_path = os.path.join(subj_dir, 'session_%s' % sess, 'figs', 'Fz_erp.pdf')
                cz_path = os.path.join(subj_dir, 'session_%s' % sess, 'figs', 'Cz_erp.pdf')
                pz_path = os.path.join(subj_dir, 'session_%s' % sess, 'figs', 'Pz_erp.pdf')
                fz = cz = pz = ''
                if os.path.exists(fz_path):
                    fz = ltx.Command('includegraphics', options=ltx.NoEscape('width=0.27\\textwidth'), arguments=ltx.NoEscape(fz_path))
                if os.path.exists(cz_path):
                    cz = ltx.Command('includegraphics', options=ltx.NoEscape('width=0.27\\textwidth'), arguments=ltx.NoEscape(cz_path))
                if os.path.exists(pz_path):
                    pz = ltx.Command('includegraphics', options=ltx.NoEscape('width=0.27\\textwidth'), arguments=ltx.NoEscape(pz_path))

                data_table.add_row([sesstext, fz, cz, pz])

    ###############
    #
    # Compile LaTeX and produce a PDF report
    #
    ###############
    doc.generate_pdf(tex_outfile, compiler='pdflatex')

    return tex_outfile + '.pdf'


if __name__ == "__main__":
    s = input('Enter a subject ID: ')
    subject_report_prelim(s)
