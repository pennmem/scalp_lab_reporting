import os
import json
import datetime as dt
from time import time
from glob import glob


def identify_modified_participants_ltpFR(day_limit=7):
    # Define parameters of experiment
    exp_dir = '/data/eeg/scalp/ltp/ltpFR/'
    naming_scheme = 'LTP[0-9][0-9][0-9]_*'
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
                                glob(os.path.join(sess_dir, 'session.log')) + \
                                glob(os.path.join(sess_dir, 'events.mat')) + \
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

    with open(os.path.join(exp_dir, 'recently_modified.json'), 'w') as f:
        json.dump(modified, f)

    return modified


def identify_modified_participants_ltpFR2(day_limit=7):

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
                                glob(os.path.join(sess_dir, 'events.mat')) + \
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

    with open(os.path.join(exp_dir, 'recently_modified.json'), 'w') as f:
        json.dump(modified, f)

    return modified


def identify_modified_participants(day_limit=7):
    """
    Identifies recently modified sessions on multiple experiments.

    :param day_limit: Sessions will be marked as recently modified if they were changed with this number of days ago.
    :return: A dictionary with experiment names mapped to their individual modified session dictionaries.
    """
    modified = dict()

    # modified['ltpFR'] = identify_modified_participants_ltpFR(day_limit)
    modified['ltpFR2'] = identify_modified_participants_ltpFR2(day_limit)

    return modified


if __name__ == "__main__":
    identify_modified_participants()
