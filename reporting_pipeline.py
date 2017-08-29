from behavioral_data_matrices import make_data_matrices_ltpFR2
from run_statistics import run_stats
from ltpFR2_report import subject_report_ltpFR2


def run_pipeline():
    data = make_data_matrices_ltpFR2()
    stats = run_stats(data)
    subject_report_ltpFR2(stats)


if __name__ == "__main__":
    run_pipeline()
