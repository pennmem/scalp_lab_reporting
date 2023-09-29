import numpy as np
from pylatex import Document, Tabu, Center, LargeText, Command
from pylatex.utils import bold


def bonus_report_VFFR(subj, scores, bonuses, nans_blank=True):
    """
    Takes in bonus information and produces two versions of a bonus report for a participant. First, it creates a
    tab-delimited text file, designed to provide an easy way to read bonus score information into a script/software in
    the future. Second, it uses LaTeX (via PyLaTeX) to create a PDF report that can easily be viewed by researchers
    or shown to participants.

    :param subj: A string containing the subject ID of the person for whom to make a report.
    :param scores: A session x score array. Recall scores should be in column 0, blink rates in column 1, and math
    scores in column 2.
    :param bonuses: A session x bonus array. Recall bonus should be in column 0, blink bonus in column 1, math bonus
    in column 2, and total bonus in column 3.
    :param nans_blank: Indicates whether or not to replace NaNs in the report with empty cell entries. (Default=True)
    :return: The paths to the TSV and PDF report, respectively
    """
    ###############
    #
    # Part 1: Text Report
    #
    ###############
    outfile = '/data/eeg/scalp/ltp/VFFR/bonus/%s_bonus_report.tsv' % subj

    # Create report header
    report = 'Session\tBad Trial\tTrial Bonus\tBlink Rate\tBlink Bonus\tTotal\n'

    # Fill in report
    for i in range(len(bonuses)):
        report += '%d\t%.1f%%\t$%.2f\t%s\t$%.2f\t$%.2f\n' % \
                  (i, scores[i][0], bonuses[i][0], str(scores[i][1]) + '%/' + str(scores[i][2]) + '%/' +
                   str(scores[i][3]) + '%', bonuses[i][1], bonuses[i][2])
    report += 'Total\t%.1f%%\t$%.2f\t%s\t$%.2f\t$%.2f\n' % \
              (np.nanmean([s[0] for s in scores]), np.nansum([b[0] for b in bonuses]),
               str(round(np.nanmean([s[1] for s in scores]), 1)) + '%/' +
               str(round(np.nanmean([s[2] for s in scores]), 1)) + '%/' +
               str(round(np.nanmean([s[3] for s in scores]), 1)) + '%',
               np.nansum([b[1] for b in bonuses]), np.nansum([b[2] for b in bonuses]))
    report = report.strip()

    # Replace nans with blank entries if desired
    if nans_blank:
        for s in ('$nan', 'nan%', 'nan'):
            report = report.replace(s, '')

    # Write text report
    with open(outfile, 'w') as f:
        f.write(report)

    ###############
    #
    # Part 2: PDF Report
    #
    ###############

    tex_outfile = '/data/eeg/scalp/ltp/VFFR/bonus/%s_bonus_report' % subj

    # Divide report into rows
    report = report.split('\n')
    # Create list of column names
    header = report.pop(0).split('\t')
    # Define the format of the LaTeX tabular -- one column for each item in the header
    fmt = ('X[r] ' * len(header)).strip()
    # Create LaTeX document
    geometry_options = dict(
        paperheight='7in',
        paperwidth='10in',
        margin='.5in'
    )
    doc = Document(page_numbers=False, geometry_options=geometry_options)

    with doc.create(Center()) as centered:
        doc.append(LargeText('Bonus Report: %s' % subj))
        doc.append(Command('par'))
        with centered.create(Tabu(fmt)) as data_table:
            data_table.add_row([''] * len(header))
            data_table.add_hline()
            data_table.add_row([''] * len(header))
            data_table.add_row(header, mapper=[bold])
            data_table.add_row([''] * len(header))
            data_table.add_hline()
            data_table.add_row([''] * len(header))
            for row in report[:-1]:
                data_table.add_row(row.split('\t'))
            data_table.add_row([''] * len(header))
            data_table.add_hline()
            data_table.add_row([''] * len(header))
            data_table.add_row(report[-1].split('\t'))
    doc.generate_pdf(tex_outfile, compiler='pdflatex')

    return outfile, tex_outfile + '.pdf'
