import os
import json

from bonus_reporting.calculation.bonus_ltpFR2 import calculate_bonus_ltpFR2
from bonus_reporting.calculation.bonus_SFR import calculate_bonus_SFR
from bonus_reporting.calculation.bonus_FR1_scalp import calculate_bonus_FR1_scalp
from bonus_reporting.calculation.bonus_VFFR import calculate_bonus_VFFR
from bonus_reporting.calculation.bonus_repfr import calculate_bonus_repfr
from bonus_reporting.calculation.bonus_courier import calculate_bonus_courier
from bonus_reporting.calculation.bonus_delayrepfr import calculate_bonus_delayrepfr

from bonus_reporting.reports.bonus_report_ltpFR2 import bonus_report_ltpFR2
from bonus_reporting.reports.bonus_report_SFR import bonus_report_SFR
from bonus_reporting.reports.bonus_report_FR1_scalp import bonus_report_FR1_scalp
from bonus_reporting.reports.bonus_report_VFFR import bonus_report_VFFR
from bonus_reporting.reports.bonus_report_repfr import bonus_report_repfr
from bonus_reporting.reports.bonus_report_courier import bonus_report_courier
from bonus_reporting.reports.bonus_report_delayrepfr import bonus_report_delayrepfr


def upload_bonus_report(report_path, exp):
    """
    Uploads the file at report_path to memory.psych.upenn.edu, and places it in the bonus reports folder for the
    specified experiment.

    :param report_path: The local file path to the report being uploaded.
    :param exp: The name of the experiment. Used for determining the destination path.
    """
    if os.path.exists(report_path):
        # os.system('scp %s reports@memory.psych.upenn.edu:/var/www/html/ltp_reports/%s_Bonus/' % (report_path, exp))
        pass


def run_bonus(experiment=None, subjects=None):
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
        SFR=(calculate_bonus_SFR, bonus_report_SFR, True),
        FR1_scalp=(calculate_bonus_FR1_scalp, bonus_report_FR1_scalp, True),
        VFFR=(calculate_bonus_VFFR, bonus_report_VFFR, True),
        ltpRepFR=(calculate_bonus_repfr, bonus_report_repfr, True),
        NiclsCourierReadOnly=(calculate_bonus_courier, bonus_report_courier, True),
        NiclsCourierClosedLoop=(calculate_bonus_courier,
            bonus_report_courier, True),
        ltpDelayRepFRReadOnly=(calculate_bonus_delayrepfr, bonus_report_delayrepfr, True),
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

        if not os.path.exists('/data/eeg/scalp/ltp/%s/bonus' % exp):
            print('/data/eeg/scalp/ltp/%s/bonus' % exp)
            os.makedirs('/data/eeg/scalp/ltp/%s/bonus' % exp)

        # Run on recently modified subjects unless user specified both the experiment and subjects to use
        if subjects is None or experiment is None:
            with open('/data/eeg/scalp/ltp/%s/recently_modified.json' % exp, 'r') as f:
                subjects = json.load(f).keys()

        for s in subjects:
            try:
                scores, bonuses = calculation_func(s, exp=exp)
            except:
                scores, bonuses = calculation_func(s)
            if report_func is None:
                continue
            try:
                _, pdf_path = report_func(s, scores, bonuses, exp=exp)
            except Exception as e:
                print(e)
                _, pdf_path = report_func(s, scores, bonuses)
            if upload:
                upload_bonus_report(pdf_path, exp)


if __name__ == "__main__":
    run_bonus()
