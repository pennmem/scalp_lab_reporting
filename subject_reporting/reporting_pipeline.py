from subject_reporting.run_statistics import run_stats
from subject_reporting.behavioral_data_matrices import make_data_matrices_ltpFR2
from subject_reporting.ltpFR2_report import subject_report_ltpFR2


def run_pipeline():
    make_data_matrices_ltpFR2()
    # run_stats()
    # subject_report_ltpFR2()


if __name__ == "__main__":
    run_pipeline()
