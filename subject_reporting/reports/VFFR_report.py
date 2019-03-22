import os
import numpy as np
import pylatex as ltx
from .load_stats import load_stats


def subject_report_VFFR(subj):
    """
    Create a subject report for the specified VFFR participant.

    :param subj: The subject for whom a report will be generated.
    :return: The filepath of the PDF report.
    """
    ###############
    #
    # Define parameters of experiment
    #
    ###############
    stat_dir = '/data/eeg/scalp/ltp/VFFR/behavioral/stats/'
    subj_dir = '/data/eeg/scalp/ltp/VFFR/%s/' % subj
    tex_outfile = '/data/eeg/scalp/ltp/VFFR/%s/%s_report' % (subj, subj)

    ###############
    #
    # Load session numbers from stats file
    #
    ###############

    stats = load_stats(stat_dir, subj)
    if not stats:
        return None
    sessions = np.array(stats['session'])

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

        ###############
        #
        # Create table of ERP plots
        #
        ###############
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

            # Add a row containing the cross-session average ERPs
            sesstext = ltx.Command('raisebox', arguments=[ltx.NoEscape('0.067\\textwidth'), 'Average'])
            fz_path = os.path.join(subj_dir, 'figs', 'Fz_erp.pdf')
            cz_path = os.path.join(subj_dir, 'figs', 'Cz_erp.pdf')
            pz_path = os.path.join(subj_dir, 'figs', 'Pz_erp.pdf')
            fz = cz = pz = ''
            if os.path.exists(fz_path):
                fz = ltx.Command('includegraphics', options=ltx.NoEscape('width=0.3\\textwidth'),
                                 arguments=ltx.NoEscape(fz_path))
            if os.path.exists(cz_path):
                cz = ltx.Command('includegraphics', options=ltx.NoEscape('width=0.3\\textwidth'),
                                 arguments=ltx.NoEscape(cz_path))
            if os.path.exists(pz_path):
                pz = ltx.Command('includegraphics', options=ltx.NoEscape('width=0.3\\textwidth'),
                                 arguments=ltx.NoEscape(pz_path))
            data_table.add_row([sesstext, fz, cz, pz])

            # Add one row of ERPs for each session
            for i, sess in enumerate(sessions):
                sesstext = ltx.Command('raisebox', arguments=[ltx.NoEscape('0.067\\textwidth'), sess])
                fz_path = os.path.join(subj_dir, 'session_%s' % sess, 'figs', 'Fz_erp.pdf')
                cz_path = os.path.join(subj_dir, 'session_%s' % sess, 'figs', 'Cz_erp.pdf')
                pz_path = os.path.join(subj_dir, 'session_%s' % sess, 'figs', 'Pz_erp.pdf')
                fz = cz = pz = ''
                if os.path.exists(fz_path):
                    fz = ltx.Command('includegraphics', options=ltx.NoEscape('width=0.3\\textwidth'), arguments=ltx.NoEscape(fz_path))
                if os.path.exists(cz_path):
                    cz = ltx.Command('includegraphics', options=ltx.NoEscape('width=0.3\\textwidth'), arguments=ltx.NoEscape(cz_path))
                if os.path.exists(pz_path):
                    pz = ltx.Command('includegraphics', options=ltx.NoEscape('width=0.3\\textwidth'), arguments=ltx.NoEscape(pz_path))

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
    subject_report_VFFR(s)
