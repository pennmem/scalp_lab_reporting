import os
import json
from subject_reporting.behavioral.behavioral_matrices_ltpFR2 import make_data_matrices_ltpFR2
from subject_reporting.statistics.ltpFR2_stats import run_stats_ltpFR2
from subject_reporting.erp.ltpFR2_ERP import erp_ltpFR2
from subject_reporting.reports.ltpFR2_report import subject_report_ltpFR2


def upload_subject_report(report_path, exp):
    """
    Uploads the file at report_path to memory.psych.upenn.edu, and places it in the bonus reports folder for the
    specified experiment.

    :param report_path: The local file path to the report being uploaded.
    :param exp: The name of the experiment. Used for determining the destination path.
    """
    os.system('scp %s reports@memory.psych.upenn.edu:/var/www/html/ltp_reports/%s/' % (report_path, exp))


def run_pipeline(exp, subjects=None, upload=True):
    """
    Runs the subject report pipeline on a list of participants. The pipeline has three major steps:
    1) Create behavioral data matrices containing presentation and recall information needed for analyses.
    2) Run a set of standard statistics on the recall data (e.g. SPC, lag-CRP, etc.)
    3) Generate a PDF subject report, containing relevant statistics and performance information, then upload to Memory.

    Step 1 creates JSON files containing the behavioral matrices for each participant in
    /data/eeg/scalp/ltp/<exp_name>/behavioral/data/

    Step 2 creates JSON files containing the statistics for each participant in
    /data/eeg/scalp/ltp/<exp_name>/behavioral/stats/

    Step 3 creates a PDF report for each participant in
    /data/eeg/scalp/ltp/<exp_name>/report/

    :param exp: The name of the experiment for which to generate reports.
    :param subjects: A list of subject IDs on whom to run the reporting pipeline. If None, run on all recently modified
    participants in the target experiment.
    :param upload: Indicates whether or not reports should be uploaded to memory.psych.upenn.edu after being generated.
    """

    ###############
    #
    # Determine list of participants to run
    #
    ###############
    if subjects is None:
        with open('/data/eeg/scalp/ltp/%s/recently_modified.json' % exp, 'r') as f:
            subjects = json.load(f).keys()
    elif subjects == 'all':
        # TODO: Add support for running on all subjects
        subjects = []

    ###############
    #
    # ltpFR2 Reporting Pipeline
    #
    ###############
    if exp == 'ltpFR2':
        for s in subjects:
            beh_data = make_data_matrices_ltpFR2(s)
            # Skip participant if they haven't actually completed any sessions
            if beh_data == {}:
                continue
            run_stats_ltpFR2(s, data=beh_data)
            # erp_ltpFR2(s)
            # report_path = subject_report_ltpFR2(s)
            # if upload:
            #   upload_subject_report(report_path, exp)


if __name__ == "__main__":
    run_pipeline('ltpFR2')
