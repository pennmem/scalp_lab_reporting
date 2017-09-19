import numpy as np


def make_serialpos_matrix(pres_nos, rec_nos):
    """
    Create a serial position of recalls matrix based on presented and recalled item information.

    :param pres_nos: A trials x presentation matrix of presented item IDs.
    :param rec_nos: A trials x recall matrix of recalled item IDs.
    :return: A trials x recall matrix of recalled item serial positions.
    """
    serialpos = np.zeros_like(rec_nos, dtype='int16')

    for i in range(pres_nos.shape[0]):
        for j, recall in enumerate(rec_nos[i, :]):
            if recall == 0:
                continue

            positions = np.where(pres_nos[i, :] == recall)[0]

            if len(positions) > 1:
                # print('WARNING: A word was presented multiple times!')
                return None
            elif len(positions) == 1:
                serialpos[i, j] = positions[0] + 1
            else:
                serialpos[i, j] = -1

    return serialpos
