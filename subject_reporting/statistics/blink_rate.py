import numpy as np


def calc_blink_rate(blinks, sessions):
    """
    Scores an array of blink rates consisting of [left b.r., right b.r., any b.r.].

    :param blinks: A trials x items matrix of blink information.
    :param sessions: An array indicating which session each row of blinks originates from.
    :return: A sessions x 3 matrix of blink rates consisting of [left b.r., right b.r., any b.r.] for each session
    """
    usess = np.unique(sessions)
    br = np.zeros((len(usess), 3))

    for sess_num in usess:

        # Select trials from one session
        sess_blinks = blinks[sessions == sess_num]

        # Drop unaligned events
        sess_blinks = sess_blinks[sess_blinks >= 0]

        # Fill in blink rates for one session in order: [left b.r., right b.r., any b.r.]
        if len(sess_blinks) > 0:
            br[sess_num, 0] = np.mean((sess_blinks == 1) | (sess_blinks == 3))
            br[sess_num, 1] = np.mean(sess_blinks >= 2)
            br[sess_num, 2] = np.mean(sess_blinks >= 1)
        else:
            br[sess_num, :].fill(np.nan)

    return br
