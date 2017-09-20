import numpy as np

def p_rec(recalled, subjects):
    """
    Calculate the overall probability of recall for each subject.

    :param recalled: A trial x item matrix indicating whether each presented item on each trial was correctly recalled.
    :param subjects: An array indicating which subject performed each trial.
    :return: An array containing the probability of recall for each unique subject.
    """

    usub = np.unique(subjects)
    result = [recalled[subjects == subj].mean() for subj in usub]

    return result