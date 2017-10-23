import os
import re
import numpy as np
from glob import glob


def calculate_bonus_SFR(subj):
    """
    Calculates bonus payments for each of a participant's sessions based on the following performance brackets:

    P-Recs:
    $0 --> 0% - 34.99%
    $1 --> 35% - 46.99%
    $2 --> 47% - 60.99%
    $3 --> 61% - 69.99%
    $4 --> 70% - 82.99%
    $5 --> 83% - 100%

    Math Correct:
    $0 --> < 118
    $1 --> 118 - 126
    $2 --> 127 - 146
    $3 --> 147 - 156
    $4 --> 157 - 176
    $5 --> > 177

    Recall scores and bonuses can only be calculated once the session has been annotated.

    :param subj: A string containing the subject ID of the participant for whom to calculate bonuses.
    :return: Returns two numpy arrays. The first is a session x score matrix, with prec in column 0
    and math score in column 1. The second is a session x bonus matrix, with recall bonus in column 0,
    math bonus in column 1, and total bonus in column 2.
    """

    # Set experiment parameters and performance bracket boundaries
    n_sessions = 2
    n_trials = 26
    brackets = dict(
        prec=[35, 47, 61, 70, 83],
        mc=[118, 127, 147, 157, 177]
    )

    scores = np.zeros((n_sessions, 2))
    bonuses = np.zeros((n_sessions, 3))

    for sess in range(n_sessions):
        sess_dir = '/data/eeg/scalp/ltp/SFR/%s/session_%d/' % (subj, sess)
        sess_precs = []
        lsts = glob(os.path.join(sess_dir, '*.lst'))
        for lst in lsts:
            par = os.path.splitext(lst)[0] + '.par'
            with open(lst, 'r') as f:
                pres = [w.strip() for w in f.readlines()]
            if os.path.exists(par):
                with open(par, 'r') as f:
                    rec = [w.split('\t')[2].strip() for w in f.readlines()]
                    recalled = [(w in rec) for w in pres]
                    sess_precs.append(np.mean(recalled))
        prec = np.mean(sess_precs) * 100 if len(sess_precs) == len(lsts) else np.nan  # Leave as nan if any missing annotations

        log = glob(os.path.join(sess_dir, '*.json'))
        if len(log) == 0:
            mc = np.nan
        else:
            mc = 0
            for l in log:
                with open(l, 'r') as f:
                    log_text = f.read()
                mc += len([x for x in re.finditer('"correctness":true', log_text)])

        # Calculate bonuses based on performance brackets
        prec_bonus = np.searchsorted(brackets['prec'], prec, side='right') if not np.isnan(prec) else np.nan
        math_bonus = np.searchsorted(brackets['mc'], mc, side='right') if not np.isnan(mc) else np.nan
        total_bonus = prec_bonus + math_bonus

        # Record scores and bonuses from session
        scores[sess] = [prec, mc]
        bonuses[sess] = [prec_bonus, math_bonus, total_bonus]

    return scores, bonuses


if __name__=="__main__":
    s = input('Please enter a subject number: ')
    print(calculate_bonus_SFR(s))
