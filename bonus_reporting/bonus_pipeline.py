import os
import json
from bonus_reporting.calculation.bonus_ltpFR2 import calculate_bonus_ltpFR2
from bonus_reporting.reports.bonus_report_ltpFR2 import bonus_report_ltpFR2


def upload_bonus_report(report_path, exp):
    """
    Uploads the file at report_path to memory.psych.upenn.edu, and places it in the bonus reports folder for the
    specified experiment.

    :param report_path: The local file path to the report being uploaded.
    :param exp: The name of the experiment. Used for determining the destination path.
    """
    os.system('scp %s reports@memory.psych.upenn.edu:/var/www/html/ltp_reports/%s_Bonus/' % (report_path, exp))


def run_bonus(exp, subjects=None, upload=True):
    """
    Runs the bonus pipeline on a list of subjects. First calculates the performance scores and bonus payments for each
    of the participants' sessions, then generates a report for each participant.

    :param exp: The name of the experiment in which the subjects were run.
    :param subjects: A list of subject IDs on whom to run the bonus reporting pipeline.
    :param upload: Indicates whether or not reports should be uploaded to memory.psych.upenn.edu after being generated.
    """
    if subjects is None:
        with open('/data/eeg/scalp/ltp/%s/recently_modified.json' % exp, 'r') as f:
            subjects = json.load(f).keys()

    # ltpFR2 reporting
    if exp == 'ltpFR2':
        for s in subjects:
            scores, bonuses = calculate_bonus_ltpFR2(s)
            _, pdf_path = bonus_report_ltpFR2(s, scores, bonuses)
            if upload:
                upload_bonus_report(pdf_path, exp)
    else:
        raise Exception('Experiment name not recognized!')


if __name__ == "__main__":
    run_bonus('ltpFR2')
