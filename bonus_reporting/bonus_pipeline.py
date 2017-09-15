from bonus_reporting.calculation.bonus_ltpFR2 import calculate_bonus_ltpFR2
from bonus_reporting.reports.bonus_report_ltpFR2 import bonus_report_ltpFR2


def run_bonus(subjects, exp):
    """
    Runs the bonus pipeline on a list of subjects. First calculates the performance scores and bonus payments for each
    of the participants' sessions, then generates a report for each participant.

    :param subjects: A list of subject IDs on whom to run the bonus reporting pipeline.
    :param exp: The name of the experiment in which the subjects were run.
    """
    # ltpFR2 reporting
    if exp == 'ltpFR2':
        for s in subjects:
            scores, bonuses = calculate_bonus_ltpFR2(s)
            bonus_report_ltpFR2(s, scores, bonuses)


if __name__ == "__main__":
    run_bonus(['LTP341', 'LTP366', 'LTP367', 'LTP368', 'LTP369', 'LTP370', 'LTP371', 'LTP372', 'LTP373'], exp='ltpFR2')
