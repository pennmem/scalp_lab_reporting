import os
import json
import datetime as dt
from time import time
from glob import glob


def identify_modified_participants_ltpFR2(day_limit=7):
    """
    Identifies any ltpFR2 sessions with *.ann, session.log, or *.bz2 (eeg) files that have been changed in
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
                                glob(os.path.join(sess_dir, 'session.log')) + \
                                glob(os.path.join(sess_dir, 'eeg', '*.bz2'))

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


def identify_modified_participants_SFR(day_limit=7):
    """
    Identifies any SFR sessions with *.ann, *.json, or *.wav files that have been changed in
    the last day_limit days. Creates a json file containing a dictionary with one entry for each participant with at
    least 1 recently modified session, containing a list of which session numbers have recently been modified.

    :param day_limit: The maximum number of days since last modification that is considered to be recently modified.
    :return: A dictionary with recently modified participants' IDs mapped to their recently modified sessions.
    """
    # Define parameters of experiment
    exp_dir = '/data/eeg/scalp/ltp/SFR/'
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


def identify_modified_participants_FR1_scalp(day_limit=7):
    """
    Identifies any FR1_scalp sessions with *.ann, *.json, or *.wav files that have been changed in
    the last day_limit days. Creates a json file containing a dictionary with one entry for each participant with at
    least 1 recently modified session, containing a list of which session numbers have recently been modified.

    :param day_limit: The maximum number of days since last modification that is considered to be recently modified.
    :return: A dictionary with recently modified participants' IDs mapped to their recently modified sessions.
    """
    # Define parameters of experiment
    exp_dir = '/data/eeg/scalp/ltp/FR1_scalp/'
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


def identify_modified_participants(day_limit=7):
    """
    Identifies recently modified sessions on multiple experiments.

    :param day_limit: Sessions will be marked as recently modified if they were changed with this number of days ago.
    :return: A dictionary with experiment names mapped to their individual modified session dictionaries.
    """
    IDENTIFIERS = dict(
        ltpFR2=identify_modified_participants_ltpFR2,
        SFR=identify_modified_participants_SFR,
        FR1_scalp=identify_modified_participants_FR1_scalp
    )

    with open('/data/eeg/scalp/ltp/ACTIVE_EXPERIMENTS.txt', 'r') as f:
        experiments = [s.strip() for s in f.readlines() if s.strip() in IDENTIFIERS]

    for exp in experiments:
        modified = IDENTIFIERS[exp](day_limit)
        with open('/data/eeg/scalp/ltp/%s/recently_modified.json' % exp, 'w') as f:
            json.dump(modified, f)


if __name__ == "__main__":
    identify_modified_participants()
