import os
import json
import datetime as dt
from time import time
from glob import glob


def identify_modified_participants_ltpFR(day_limit=7):
    """
    Identifies any ltpFR2 sessions with *.ann, session.log, or *.raw/*.mff/*.bdf (eeg) files that have been changed in
    the last day_limit days. Creates a json file containing a dictionary with one entry for each participant with at
    least 1 recently modified session, containing a list of which session numbers have recently been modified.

    :param day_limit: The maximum number of days since last modification that is considered to be recently modified.
    :return: A dictionary with recently modified participants' IDs mapped to their recently modified sessions.
    """
    # Define parameters of experiment
    exp_dir = '/data/eeg/scalp/ltp/ltpFR/'
    naming_scheme = 'LTP[0-9][0-9][0-9](_[0-9][0-9])?'
    n_sess = 20
    sessions = range(n_sess)

    # Find all ltpFR2 subject directories
    subj_dirs = glob(os.path.join(exp_dir, naming_scheme))

    # Get current timestamp
    current_time = dt.datetime.fromtimestamp(time())

    # Determine which sessions from each subject have been modified
    modified = dict()
    for path in subj_dirs:
        subj = os.path.basename(path)
        for i in sessions:
            # Locate files to check for modifications
            sess_dir = os.path.join(path, 'session_%d' % i)
            files_of_interest = glob(os.path.join(sess_dir, '*.ann')) + \
                                glob(os.path.join(sess_dir, '*.par')) + \
                                glob(os.path.join(sess_dir, 'session.log')) + \
                                glob(os.path.join(sess_dir, 'eeg', '*.bdf')) + \
                                glob(os.path.join(sess_dir, 'eeg', '*.mff')) + \
                                glob(os.path.join(sess_dir, 'eeg', '*.raw'))

            # Check each file for recent modifications
            for f in files_of_interest:
                last_modified = dt.datetime.fromtimestamp(os.path.getmtime(f))
                days_since_modification = (current_time - last_modified).days
                # Record modified subjects and sessions in a dictionary
                if days_since_modification < day_limit:
                    if subj not in modified:
                        modified[subj] = [i]
                    else:
                        modified[subj].append(i)
                    break

    return modified


def identify_modified_participants_ltpFR2(day_limit=7):
    """
    Identifies any ltpFR2 sessions with *.ann, session.log, or *.raw/*.mff/*.bdf (eeg) files that have been changed in
    the last day_limit days. Creates a json file containing a dictionary with one entry for each participant with at
    least 1 recently modified session, containing a list of which session numbers have recently been modified.

    :param day_limit: The maximum number of days since last modification that is considered to be recently modified.
    :return: A dictionary with recently modified participants' IDs mapped to their recently modified sessions.
    """
    # Define parameters of experiment
    exp_dir = '/data/eeg/scalp/ltp/ltpFR2/'
    naming_scheme = 'LTP[0-9][0-9][0-9]'
    n_sess = 24
    sessions = range(n_sess)

    # Find all ltpFR2 subject directories
    subj_dirs = glob(os.path.join(exp_dir, naming_scheme))

    # Get current timestamp
    current_time = dt.datetime.fromtimestamp(time())

    # Determine which sessions from each subject have been modified
    modified = dict()
    for path in subj_dirs:
        subj = os.path.basename(path)
        for i in sessions:
            # Locate files to check for modifications
            sess_dir = os.path.join(path, 'session_%d' % i)
            files_of_interest = glob(os.path.join(sess_dir, '*.ann')) + \
                                glob(os.path.join(sess_dir, '*.par')) + \
                                glob(os.path.join(sess_dir, 'session.log')) + \
                                glob(os.path.join(sess_dir, 'eeg', '*.bdf')) + \
                                glob(os.path.join(sess_dir, 'eeg', '*.mff')) + \
                                glob(os.path.join(sess_dir, 'eeg', '*.raw'))

            # Check each file for recent modifications
            for f in files_of_interest:
                last_modified = dt.datetime.fromtimestamp(os.path.getmtime(f))
                days_since_modification = (current_time - last_modified).days
                # Record modified subjects and sessions in a dictionary
                if days_since_modification < day_limit:
                    if subj not in modified:
                        modified[subj] = [i]
                    else:
                        modified[subj].append(i)
                    break

    return modified


def identify_modified_participants_RAA(exp, day_limit=7):
    """
    Identifies any SFR/FR1_scalp sessions with *.ann, *.json, or *.wav files that have been changed in
    the last day_limit days. Creates a json file containing a dictionary with one entry for each participant with at
    least 1 recently modified session, containing a list of which session numbers have recently been modified.

    :param exp: A string indicating whether the session was "SFR" or "FR1_scalp".
    :param day_limit: The maximum number of days since last modification that is considered to be recently modified.
    :return: A dictionary with recently modified participants' IDs mapped to their recently modified sessions.
    """
    # Define parameters of experiment
    exp_dir = '/data/eeg/scalp/ltp/%s/' % exp
    naming_scheme = 'RAA[0-9][0-9][0-9]'
    n_sess = 2
    sessions = range(n_sess)

    # Find all ltpFR2 subject directories
    subj_dirs = glob(os.path.join(exp_dir, naming_scheme))

    # Get current timestamp
    current_time = dt.datetime.fromtimestamp(time())

    # Determine which sessions from each subject have been modified
    modified = dict()
    for path in subj_dirs:
        subj = os.path.basename(path)
        for i in sessions:
            # Locate files to check for modifications
            sess_dir = os.path.join(path, 'session_%d' % i)
            files_of_interest = glob(os.path.join(sess_dir, '*.ann')) + \
                                glob(os.path.join(sess_dir, '*.par')) + \
                                glob(os.path.join(sess_dir, '*.json')) + \
                                glob(os.path.join(sess_dir, '*.wav'))

            # Check each file for recent modifications
            for f in files_of_interest:
                last_modified = dt.datetime.fromtimestamp(os.path.getmtime(f))
                days_since_modification = (current_time - last_modified).days
                # Record modified subjects and sessions in a dictionary
                if days_since_modification < day_limit:
                    if subj not in modified:
                        modified[subj] = [i]
                    else:
                        modified[subj].append(i)
                    break

    return modified


def identify_modified_participants_unity(exp, naming_scheme, n_sess, day_limit=7):
    """
    Identifies any VFFR sessions with *.ann/.par, session.jsonl, or *.bdf files that have been changed in
    the last day_limit days. Creates a json file containing a dictionary with one entry for each participant with at
    least 1 recently modified session, containing a list of which session numbers have recently been modified.

    :param day_limit: The maximum number of days since last modification that is considered to be recently modified.
    :return: A dictionary with recently modified participants' IDs mapped to their recently modified sessions.
    """
    # Define parameters of experiment
    exp_dir = '/data/eeg/scalp/ltp/%s/' % exp
    sessions = range(n_sess)

    # Find all ltpFR2 subject directories
    subj_dirs = glob(os.path.join(exp_dir, naming_scheme))

    # Get current timestamp
    current_time = dt.datetime.fromtimestamp(time())

    # Determine which sessions from each subject have been modified
    modified = dict()
    for path in subj_dirs:
        subj = os.path.basename(path)
        for i in sessions:
            # Locate files to check for modifications
            sess_dir = os.path.join(path, 'session_%d' % i)
            files_of_interest = glob(os.path.join(sess_dir, '*.ann')) + \
                                glob(os.path.join(sess_dir, '*.par')) + \
                                glob(os.path.join(sess_dir, 'session.jsonl')) + \
                                glob(os.path.join(sess_dir, 'eeg', '*.bdf'))

            # Check each file for recent modifications
            for f in files_of_interest:
                last_modified = dt.datetime.fromtimestamp(os.path.getmtime(f))
                days_since_modification = (current_time - last_modified).days
                # Record modified subjects and sessions in a dictionary
                if days_since_modification < day_limit:
                    if subj not in modified:
                        modified[subj] = [i]
                    else:
                        modified[subj].append(i)
                    break

    return modified


def identify_modified_participants(day_limit=7):
    """
    Identifies recently modified sessions on multiple experiments.

    :param day_limit: Sessions will be marked as recently modified if they were changed with this number of days ago.
    :return: A dictionary with experiment names mapped to their individual modified session dictionaries.
    """
    IDENTIFIERS = dict(
        ltpFR=identify_modified_participants_ltpFR,
        ltpFR2=identify_modified_participants_ltpFR2,
        SFR=[identify_modified_participants_RAA, 'SFR'],
        FR1_scalp=[identify_modified_participants_RAA, 'FR1_scalp'],
        VFFR=[identify_modified_participants_unity, 'VFFR', 'LTP[0-9][0-9][0-9]', 10],
        prelim=[identify_modified_participants_unity, 'prelim', 'PLTP[0-9][0-9][0-9]', 1],
        ltpRepFR=[identify_modified_participants_unity, 'ltpRepFR', 'LTP[0-8][0-9][0-9]', 10],
        NiclsCourierReadOnly=[identify_modified_participants_unity,
            'NiclsCourierReadOnly', 'LTP[0-8][0-9][0-9]', 8],
        NiclsCourierClosedLoop=[identify_modified_participants_unity,
            'NiclsCourierClosedLoop', 'LTP[0-8][0-9][0-9]', 8]
    )

    with open('/data/eeg/scalp/ltp/ACTIVE_EXPERIMENTS.txt', 'r') as f:
        experiments = [s.strip() for s in f.readlines() if s.strip() in IDENTIFIERS]

    for exp in experiments:
        if callable(IDENTIFIERS[exp]):
            modified = IDENTIFIERS[exp](day_limit)
        else:
            func = IDENTIFIERS[exp][0]
            inputs = IDENTIFIERS[exp][1:]
            modified = func(*inputs, day_limit)
        with open('/data/eeg/scalp/ltp/%s/recently_modified.json' % exp, 'w') as f:
            json.dump(modified, f)


if __name__ == "__main__":
    day_limit = 40
    identify_modified_participants(day_limit)
