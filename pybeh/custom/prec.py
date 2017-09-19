import numpy as np


def prec(was_recalled, subjects):
    """
    Calculate the overall probability of recall for each subject, given a lists x items matrix where 0s indicate
    words that were not subsequently recalled and 1s indicate words that were subsequently recalled. Item (i, j)
    should indicate whether the jth word presented in list i was recalled.

    :param was_recalled: A lists x items matrix, indicating whether each presented word was subsequently recalled
    :param subjects: A list of subject codes, indicating which subject produced each row of was_recalled
    :return: An array containing the overall probability of recall for each unique participant
    """
    if len(was_recalled) == 0:
        return []
    usub = np.unique(subjects)
    result = np.zeros(len(usub))
    for i, s in enumerate(usub):
        result[i] = float(len(np.where(was_recalled[np.where(subjects == s)] == 1)[0])) / len(
            np.where(np.logical_not(np.isnan(was_recalled[np.where(subjects == s)])))[0])

    return result
