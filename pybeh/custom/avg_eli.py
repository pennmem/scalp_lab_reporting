import numpy as np


def avg_eli(intrusions=None, subjects=None):
    """
    A modification of the behavioral toolbox's xli function. Calculate's each partcipant's average number of ELIs per
    list instead of their total number of ELIs.
    :param intrusions: An intrusions matrix in the format generated by recalls_to_intrusions
    :param subjects: A list of subject codes, indicating which subject produced each row of the intrusions matrix
    :return: An array where each entry is the average number of PLIs per list for a single participant.
    """
    usub = np.unique(subjects)
    result = np.zeros(len(usub))
    for subject_index in range(len(usub)):
        count = 0.
        lists = 0.
        for subj in range(len(subjects)):
            if subjects[subj] == usub[subject_index]:
                lists += 1
                for serial_pos in range(len(intrusions[0])):
                    if intrusions[subj][serial_pos] < 0:
                        count += 1
        result[subject_index] = count / lists if lists > 0 else np.nan

    return result