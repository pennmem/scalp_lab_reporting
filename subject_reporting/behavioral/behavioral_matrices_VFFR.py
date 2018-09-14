import os
import json
import numpy as np


def make_data_matrices_VFFR(subj):
    """
    Creates behavioral data matrices for VFFR participants. These include the following:
    - Subject (subject)
    - Session (session)
    - Presented words (pres_words)
    - Presented word IDs (pres_nos)
    - Recalled words (rec_words)
    - Recalled word IDs (rec_nos)
    - "Recalled" matrix (whether each presented item was recalled during initial free recall) (recalled)
    - "Times" matrix (number of ms after start of initial recall that each recall was made) (times)
    - "Intrusions" matrix (whether each recall was an intrusion: ELI = -1, PLI = n > 0 -- note that PLIs are impossible
    in VFFR, but we should still maintain the standard intrusion matrix format) (intrusions)

    Also creates a subject array and a session array for each participant. Each of these contain one entry for each row
    of the behavioral matrices, and are used to record which participant performed that trial and the session during
    which session the trial occurred.

    :param subj: A string containing the subject ID for a participant.
    :return: A dictionary containing each of the data matrices for the specified participant.
    """

    ###############
    #
    # Define parameters of experiment
    #
    ###############
    exp_dir = '/data/eeg/scalp/ltp/VFFR/'
    out_dir = '/data/eeg/scalp/ltp/VFFR/behavioral/data/'
    n_practice_words = 10
    n_words = 576
    list_length = n_practice_words + n_words
    n_lists = 1
    n_sess = 10
    recalls_allowed = list_length * 2

    ###############
    #
    # Identify sessions to process
    #
    ###############

    sess_dirs = []
    for i in range(n_sess):
        sess_path = os.path.join(exp_dir, subj, 'session_%d' % i)
        if os.path.exists(os.path.join(sess_path, '575.wav')):
            sess_dirs.append(sess_path)
    if len(sess_dirs) == 0:
        return dict()

    ###############
    #
    # Create behavioral matrices for each participant
    #
    ###############
    # Get list of sessions this participant has completed, count them, and figure out the total number of lists
    n_sessions_run = len(sess_dirs)
    total_lists = n_lists * n_sessions_run

    # Create subject and session number arrays
    subj_array = [subj] * total_lists
    sess_array = []
    for i in range(n_sessions_run):
        for j in range(n_lists):
            sess_array.append(i)

    # Load subject's wordpool
    wordpool = np.loadtxt(os.path.join(exp_dir, 'full_ltp_wordpool.txt'), dtype='S32')

    # Initialize behavioral data matrices
    pres_words = np.zeros((total_lists, list_length), dtype='U32')
    pres_nos = np.zeros((total_lists, list_length), dtype='int16')
    rec_words = np.zeros((total_lists, recalls_allowed), dtype='U32')
    rec_nos = np.zeros((total_lists, recalls_allowed), dtype='int16')
    recalled = np.zeros((total_lists, list_length), dtype='float16')
    times = np.zeros((total_lists, recalls_allowed), dtype='int32')
    intru = np.zeros((total_lists, recalls_allowed), dtype='int16')

    # Create data matrices for each session
    for sess_num, session_dir in enumerate(sess_dirs):
        print('Processing session %s...' % sess_num)

        sess_pres_words = np.zeros(list_length, dtype='U32')
        sess_pres_nos = np.zeros(list_length, dtype='int16')
        sess_rec_words = np.zeros(recalls_allowed, dtype='U32')
        sess_rec_nos = np.zeros(recalls_allowed, dtype='int16')
        sess_times = np.zeros(recalls_allowed, dtype='int32')

        # Load presented from that session's .lst files (VFFR has one .lst for each word)
        for i in range(n_practice_words):
            lst_path = os.path.join(session_dir, '%d_practice.lst' % i)
            word = np.char.strip(np.loadtxt(lst_path, delimiter='\t', dtype='S32').view(np.chararray).decode('utf-8'))
            sess_pres_words[i] = word
            sess_pres_nos[i] = -1
        for i in range(n_words):
            lst_path = os.path.join(session_dir, '%d.lst' % i)
            word = np.char.strip(np.loadtxt(lst_path, delimiter='\t', dtype='S32').view(np.chararray).decode('utf-8'))
            sess_pres_words[i+n_practice_words] = word
            sess_pres_nos[i+n_practice_words] = np.searchsorted(wordpool, word) + 1

        # Load initial free recall annotations if the current session has them
        ann_path = os.path.join(session_dir, 'ffr.ann')
        if os.path.exists(ann_path):
            recs = np.atleast_2d(np.loadtxt(os.path.join(session_dir, 'ffr.ann'), delimiter='\t', dtype='S32').view(np.chararray).decode('utf-8'))
            recs = recs[recs[:, 0].astype(float) > 0]  # Drop any recalls with a negative rectime

            # We can skip the steps below for sessions with no recalls, which will produce recs of shape (1, 0)
            if recs.shape[1] >= 3:
                recs = np.char.strip(recs)
                recs = recs[(recs[:, 2] != 'VV') & (recs[:, 2] != '<>') & (recs[:, 2] != '!')]
                sess_rec_words[:len(recs)] = recs[:, 2]
                sess_rec_nos[:len(recs)] = recs[:, 1]
                sess_times[:len(recs)] = recs[:, 0].astype(float).astype(int)  # ValueError if just using .astype(int)

        # Determine whether each word was recalled during initial free recall
        sess_recalled = np.in1d(sess_pres_words, sess_rec_words)

        # Create matrix with intrusion info; ELIs are any words that were not presented -- mark these as -1
        sess_intru = ((sess_rec_words != '') & (~np.in1d(sess_rec_words, sess_pres_words))).astype(int) * -1

        # Place that session's behavioral data into the appropriate row of the subject's full data matrices
        matrix_pairs = [(pres_words, sess_pres_words), (pres_nos, sess_pres_nos), (rec_words, sess_rec_words),
                     (rec_nos, sess_rec_nos), (recalled, sess_recalled), (times, sess_times), (intru, sess_intru)]
        for pair in matrix_pairs:
            pair[0][sess_num, :] = pair[1]

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
    intru = intru[:, :max_recalls]

    # Once all of a subject's data has been processed, add their completed data matrices to the data dictionary
    data = dict(
        subject=subj_array,
        session=sess_array,
        pres_words=pres_words.tolist(),
        pres_nos=pres_nos.tolist(),
        rec_words=rec_words.tolist(),
        rec_nos=rec_nos.tolist(),
        recalled=recalled.tolist(),
        times=times.tolist(),
        intrusions=intru.tolist()
    )

    # Define location where the subject's data will be saved. Participants without 10 sessions will have their data
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
    make_data_matrices_VFFR(s)
