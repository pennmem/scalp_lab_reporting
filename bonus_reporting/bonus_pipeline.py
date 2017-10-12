import os
import json
from bonus_reporting.calculation.bonus_ltpFR2 import calculate_bonus_ltpFR2
from bonus_reporting.calculation.bonus_SFR import calculate_bonus_SFR
from bonus_reporting.calculation.bonus_FR1_scalp import calculate_bonus_FR1_scalp
from bonus_reporting.reports.bonus_report_ltpFR2 import bonus_report_ltpFR2
from bonus_reporting.reports.bonus_report_SFR import bonus_report_SFR
from bonus_reporting.reports.bonus_report_FR1_scalp import bonus_report_FR1_scalp


def upload_bonus_report(report_path, exp):
    """
    Uploads the file at report_path to memory.psych.upenn.edu, and places it in the bonus reports folder for the
    specified experiment.

    :param report_path: The local file path to the report being uploaded.
    :param exp: The name of the experiment. Used for determining the destination path.
    """
    if os.path.exists(report_path):
        os.system('scp %s reports@memory.psych.upenn.edu:/var/www/html/ltp_reports/%s_Bonus/' % (report_path, exp))


def run_bonus(experiment=None, subjects=None, upload=True):
    """
    Runs the bonus pipeline on a list of subjects. First calculates the performance scores and bonus payments for each
    of the participants' sessions, then generates a report for each participant.

    :param experiment: A string containing the name of the experiment for which to run bonus reports. If None, run on
    all active experiments.
    :param subjects: A list of subject IDs on whom to run the bonus reporting pipeline. (Can only be used when
    specifying an experiment)
    :param upload: Indicates whether or not reports should be uploaded to memory.psych.upenn.edu after being generated.
    """
    # Set bonus calculation and bonus report functions to use for each supported experiment here
    BONUS_SCRIPTS = dict(
        ltpFR2=(calculate_bonus_ltpFR2, bonus_report_ltpFR2, True),
        SFR=(calculate_bonus_SFR, bonus_report_SFR, False),
        FR1_scalp=(calculate_bonus_FR1_scalp, bonus_report_FR1_scalp, False)
    )

    # Determine experiment list
    if experiment is None:
        # Load list of supported active experiments
        with open('/data/eeg/scalp/ltp/ACTIVE_EXPERIMENTS.txt', 'r') as f:
            experiments = [s.strip() for s in f.readlines() if s.strip() in BONUS_SCRIPTS]
    else:
        if experiment in BONUS_SCRIPTS:
            experiments = [experiment]
        else:
            raise('Unsupported experiment! Supported experiments are: ', BONUS_SCRIPTS.keys())

    # Run bonus reporting
    for exp in experiments:
        calculation_func = BONUS_SCRIPTS[exp][0]
        report_func = BONUS_SCRIPTS[exp][1]
        upload = BONUS_SCRIPTS[exp][2]

        # Run on recently modified subjects unless user specified both the experiment and subjects to use
        if subjects is None or experiment is None:
            with open('/data/eeg/scalp/ltp/%s/recently_modified.json' % exp, 'r') as f:
                subjects = json.load(f).keys()

        for s in subjects:
            scores, bonuses = calculation_func(s)
            if report_func is None:
                continue
            _, pdf_path = report_func(s, scores, bonuses)
            if upload:
                upload_bonus_report(pdf_path, exp)


if __name__ == "__main__":
    run_bonus()
