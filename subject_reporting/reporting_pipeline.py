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
    if os.path.exists(report_path):
        os.system('scp %s reports@memory.psych.upenn.edu:/var/www/html/ltp_reports/%s/' % (report_path, exp))


def run_pipeline(experiment=None, subjects=None, upload=True):
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

    :param experiment: A string containing the name of the experiment for which to generate reports. If None, run on all
    active experiments.
    :param subjects: A list of subject IDs on whom to run the reporting pipeline. If None, run on all recently modified
    participants in the target experiment.
    :param upload: Indicates whether or not reports should be uploaded to memory.psych.upenn.edu after being generated.
    """
    ###############
    #
    # Set reporting functions to use for each supported experiment here
    #
    ###############
    REPORTING_SCRIPTS = dict(
        ltpFR2=(make_data_matrices_ltpFR2, run_stats_ltpFR2, erp_ltpFR2, subject_report_ltpFR2)
    )

    ###############
    #
    # Determine experiment list
    #
    ###############
    if experiment is None:
        # Load list of supported active experiments
        with open('/data/eeg/scalp/ltp/ACTIVE_EXPERIMENTS.txt', 'r') as f:
            experiments = [s.strip() for s in f.readlines() if s.strip() in REPORTING_SCRIPTS]
    else:
        if experiment in REPORTING_SCRIPTS:
            experiments = [experiment]
        else:
            raise ('Unsupported experiment! Supported experiments are: ', REPORTING_SCRIPTS.keys())

    ###############
    #
    # Run subject reporting pipeline
    #
    ###############
    for exp in experiments:
        # Run on recently modified subjects unless user specified both the experiment and subjects to use
        if subjects is None or experiment is None:
            with open('/data/eeg/scalp/ltp/%s/recently_modified.json' % exp, 'r') as f:
                subjects = json.load(f).keys()

        for s in subjects:
            beh_data = REPORTING_SCRIPTS[exp][0](s)  # Create behavioral data matrices
            # Skip participant if they haven't actually completed any sessions
            if beh_data == {}:
                continue
            REPORTING_SCRIPTS[exp][1](s, data=beh_data)  # Run behavioral statistics
            REPORTING_SCRIPTS[exp][2](s)  # Generate ERP plots
            report_path = REPORTING_SCRIPTS[exp][3](s)  # Create subject report
            if upload:
                upload_subject_report(report_path, exp)


if __name__ == "__main__":
    run_pipeline()
