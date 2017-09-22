import os
import json
import numpy as np
from pybeh.create_intrusions import intrusions as make_intrusions_matrix


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


def make_data_matrices_ltpFR2(subj):
    """
    Creates behavioral data matrices for ltpFR2 participants. These include the following:
    - Presented words
    - Presented word IDs
    - Recalled words
    - Recalled word IDs
    - "Recalled" matrix (whether each presented item was correctly recalled)
    - "Times" matrix (number of ms after start of recall period that each recall was made)
    - "Serialpos" matrix (the original serial position of each recalled word)
    - "Intrusions" matrix (whether each recall was an intrusion, and if so which type: ELI = -1, PLI = n > 0 )

    Also creates a subject array, a session array, and a bad trial array for each participant. Each of these contain
    one entry for each row of the behavioral matrices, and are used to record which participant performed that trial,
    which session the trial occurred during, and whether that trial's data is known to be bad and should be excluded.

    Consider adding the following extra matrices:
    - "Intruded" matrix
    - Distractor duration matrix

    :param run_all: If true, generate behavioral matrices for all ltpFR2 participants. If false, only generate matrices
    for recently modified participants (based on what is written in recently_modified.json). Default is false.
    :return: A dictionary with one entry for each participant processed, with a participant's entry being a
    sub-dictionary with all of their data matrices inside.
    """

    ###############
    #
    # Define parameters of experiment
    #
    ###############
    exp_dir = '/data/eeg/scalp/ltp/ltpFR2/'
    out_dir = '/data/eeg/scalp/ltp/ltpFR2/behavioral/data/'
    list_length = 24
    n_lists = 24
    n_sess = 24
    recalls_allowed = list_length * 3

    ###############
    #
    # Identify sessions to process
    #
    ###############

    sess_dirs = []
    for i in range(n_sess):
        sess_path = os.path.join(exp_dir, subj, 'session_%d' % i)
        if os.path.exists(os.path.join(sess_path, 'session.log')) or os.path.exists(os.path.join(sess_path, 'instruct.log')):
            sess_dirs.append(sess_path)
    if len(sess_dirs) == 0:
        return dict()

    ###############
    #
    # Create behavioral matrices for each participant
    #
    ###############

    # Create a dictionary mapping subject numbers to their data dictionary
    data = dict()

    # Get list of sessions this participant has completed, count them, and figure out the total number of lists
    n_sessions_run = len(sess_dirs)
    total_lists = n_lists * n_sessions_run

    # Create subject and session number arrays
    subj_array = [subj] * total_lists
    sess_array = []
    for i in range(n_sessions_run):
        for j in range(n_lists):
            sess_array.append(i)
    bad_list_array = np.zeros(total_lists, dtype=bool)

    # Load subject's wordpool
    wordpool = np.loadtxt(os.path.join(exp_dir, subj, 'wasnorm_wordpool.txt'), dtype='S32')

    # Initialize behavioral data matrices
    pres_words = np.zeros((total_lists, list_length), dtype='U32')
    pres_nos = np.zeros((total_lists, list_length), dtype='int16')
    rec_words = np.zeros((total_lists, recalls_allowed), dtype='U32')
    rec_nos = np.zeros((total_lists, recalls_allowed), dtype='int16')
    recalled = np.zeros((total_lists, list_length), dtype='float16')
    times = np.zeros((total_lists, recalls_allowed), dtype='int32')
    serialpos = np.zeros((total_lists, recalls_allowed), dtype='int16')

    # Create data matrices for each session
    for sess_num, session_dir in enumerate(sess_dirs):
        sess_pres_words = np.zeros((n_lists, list_length), dtype='U32')
        sess_rec_words = np.zeros((n_lists, recalls_allowed), dtype='U32')
        sess_rec_nos = np.zeros((n_lists, recalls_allowed), dtype='int16')
        sess_recalled = np.zeros((n_lists, list_length), dtype='float16')
        sess_times = np.zeros((n_lists, recalls_allowed), dtype='int32')

        # Load presented and recalled words from that session's .lst and .par files, respectively
        for i in range(n_lists):
            try:
                sess_pres_words[i, :] = np.char.strip(np.loadtxt(os.path.join(session_dir, '%d.lst' % i),
                                                        delimiter='\t', dtype='S32').view(np.chararray).decode('utf-8'))
                recs = np.atleast_2d(np.loadtxt(os.path.join(session_dir, '%d.par' % i),
                                                        delimiter='\t', dtype='S32').view(np.chararray).decode('utf-8'))
            except IOError:
                bad_list_array[sess_num * n_lists + i] = True
                sess_recalled[i, :].fill(np.nan)
                continue

            # We can skip the steps below for trials with no recalls, which will produce a recs of shape (1, 0)
            if recs.shape[1] >= 3:
                recs = np.char.strip(recs)
                recs = recs[np.where(recs[:, 2] != 'VV')]
                sess_rec_words[i, :len(recs)] = recs[:, 2]
                sess_rec_nos[i, :len(recs)] = recs[:, 1]
                sess_times[i, :len(recs)] = recs[:, 0]

        # Convert presented words to their ID numbers by referencing the full word pool (remember to add 1 to the IDs!)
        sess_pres_nos = np.searchsorted(wordpool, sess_pres_words) + 1

        # Determine whether each presented word was recalled during its own trial (does not count if only recalled
        # as a PLI in a later trial)
        for i, row in enumerate(sess_pres_words):
            for j, w in enumerate(row):
                if w in sess_rec_words[i]:
                    sess_recalled[i, j] = 1

        # Create matrix with the serial positions of recalls
        sess_serialpos = make_serialpos_matrix(sess_pres_nos, sess_rec_nos)

        # Identify first row of the current session and first row of the following session
        start_row = sess_num * n_lists
        end_row = start_row + n_lists


        mat_pairs = [(pres_words, sess_pres_words), (pres_nos, sess_pres_nos), (rec_words, sess_rec_words),
                     (rec_nos, sess_rec_nos), (recalled, sess_recalled), (times, sess_times)]
        # sess_serialpos == None occurs only if a word was presented multiple times. If this happens, mark the
        # whole session as bad and leave the serialpos matrix as zeros.
        if sess_serialpos is None:
            bad_list_array[start_row:end_row] = True
        else:
            mat_pairs.append((serialpos, sess_serialpos))

        # Place that session's behavioral data into the appropriate rows of the subject's full data matrices
        for pair in mat_pairs:
            pair[0][start_row:end_row, :] = pair[1]


    # Create matrix with intrusion info
    intrusions = make_intrusions_matrix(rec_nos, pres_nos, subj_array, sess_array)

    ###############
    #
    # Clean up matrices and write to JSON
    #
    ###############

    # Identify the max number of recalls the subject made on any trial of any session, as this is the number of
    # columns we should keep in our recall-related matrices
    recall_columns = np.where(rec_nos != 0)[1]
    max_recalls = recall_columns.max() + 1 if len(recall_columns) > 0 else 0

    # Trim unused columns of the recall-related data matrices
    rec_words = rec_words[:, :max_recalls]
    rec_nos = rec_nos[:, :max_recalls]
    times = times[:, :max_recalls]
    serialpos = serialpos[:, :max_recalls]
    intrusions = intrusions[:, :max_recalls]

    # Once all of a subject's data has been processed, add their completed data matrices to the data dictionary
    data = dict(
        subject=subj_array,
        session=sess_array,
        good_trial=np.logical_not(bad_list_array).tolist(),

        pres_words=pres_words.tolist(),
        pres_nos=pres_nos.tolist(),
        rec_words=rec_words.tolist(),
        rec_nos=rec_nos.tolist(),
        recalled=recalled.tolist(),
        times=times.tolist(),
        serialpos=serialpos.tolist(),
        intrusions=intrusions.tolist()
    )

    # Define location where the subject's data will be saved. Participants without 24 sessions will have their data
    # specially marked as incomplete
    outfile_complete = os.path.join(out_dir, 'beh_data_%s.json' % subj)
    outfile_incomplete = os.path.join(out_dir, 'beh_data_%s_incomplete.json' % subj)

    # Save data as a json file with one of two names, depending on whether the participant has finished all sessions
    if n_sessions_run == n_sess:
        with open(outfile_complete, 'w') as f:
            json.dump(data, f)
        # After the person runs their final session, we can remove the old data file labelled with "incomplete"
        if os.path.exists(outfile_incomplete):
            os.remove(outfile_incomplete)
    else:
        with open(outfile_incomplete, 'w') as f:
            json.dump(data, f)

    return data


if __name__ == "__main__":
    s = input('Enter a subject ID: ')
    make_data_matrices_ltpFR2(s)
