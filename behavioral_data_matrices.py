import os
import json
import numpy as np
from glob import glob


def make_serialpos_matrix(pres_nos, rec_nos):
    serialpos = np.zeros_like(rec_nos, dtype='int16')

    for i in range(pres_nos.shape[0]):
        for j, recall in enumerate(rec_nos[i, :]):
            if recall == 0:
                continue
            positions = np.where(pres_nos[i, :] == recall)[0]
            serialpos[i, j] = positions[0] + 1 if len(positions) != 0 else -1

    return serialpos


def make_intrusions_matrix(pres_nos, rec_nos):
    intrusions = np.zeros_like(rec_nos, dtype='int16')

    for i in range(pres_nos.shape[0]):
        for j, recall in enumerate(rec_nos[i, :]):
            if recall == 0:
                continue
            # Check if recalled word has been presented in or prior to the current trial
            pres = np.where(pres_nos[:i+1, :] == recall)[0]
            if len(pres) != 0:
                # PLIs marked as n, where n is number of lists back. Correct recalls marked as 0.
                intrusions[i, j] = i - pres[0]
            else:
                # ELIs marked as -1
                intrusions[i, j] = -1

    return intrusions


def make_data_matrices_ltpFR2():
    """ 
    Consider adding the following:
    - "Intruded" matrix
    - Distractor duration matrix
    """
    # Define parameters of experiment
    exp_dir = '/data/eeg/scalp/ltp/ltpFR2/'
    naming_scheme = 'LTP[0-9][0-9][0-9]'
    list_length = 24
    n_lists = 24
    n_sess = 24
    recalls_allowed = list_length * 3

    # Find all ltpFR2 subject directories
    subjs = glob(os.path.join(exp_dir, naming_scheme))

    # Create a dictionary of participants mapped to a list of their session directories (for completed sessions)
    session_dict = dict()
    for s in subjs:
        sess_run = []
        for i in range(n_sess):
            sess_path = os.path.join(s, 'session_%d' % i)
            if os.path.exists(os.path.join(sess_path, 'session.log')):
                sess_run.append(sess_path)
        if len(sess_run) > 0:
            session_dict[os.path.basename(s)] = sess_run

    # Create a dictionary mapping subject numbers to their data dictionary
    data = dict()
    for subj in session_dict:
        # Get list of sessions this participant has completed, count them, and figure out the total number of lists
        sessions_run = session_dict[subj]
        n_sessions_run = len(sessions_run)
        total_lists = n_lists * n_sessions_run

        # Create subject and session number arrays
        subj_array = np.array([subj] * n_sessions_run)
        sess_array = np.array(range(n_lists) * n_sessions_run)
        bad_list_array = np.zeros(total_lists, dtype=bool)

        # Load subject's wordpool
        wordpool = np.loadtxt('/data/eeg/scalp/ltp/ltpFR2/%s/wasnorm_wordpool.txt' % subj, dtype='S32')

        # Define location where the subject's data will be saved
        outfile = '/Users/jessepazdera/Desktop/behavioral/beh_data_%s.json' % subj

        if os.path.exists(outfile):
            continue

        # Initialize behavioral data matrices
        pres_words = np.zeros((total_lists, list_length), dtype='S32')
        pres_nos = np.zeros((total_lists, list_length), dtype='S32')
        rec_words = np.zeros((total_lists, recalls_allowed), dtype='S32')
        rec_nos = np.zeros((total_lists, recalls_allowed), dtype='int16')
        recalled = np.zeros((total_lists, list_length), dtype=bool)
        times = np.zeros((total_lists, recalls_allowed), dtype='int32')
        serialpos = np.zeros((total_lists, recalls_allowed), dtype='int16')
        intrusions = np.zeros((total_lists, recalls_allowed), dtype='int16')

        # Create data matrices for each session
        for sess_num, session_dir in enumerate(sessions_run):

            sess_pres_words = np.zeros((n_lists, list_length), dtype='S32')
            sess_rec_words = np.zeros((n_lists, recalls_allowed), dtype='S32')
            sess_rec_nos = np.zeros((n_lists, recalls_allowed), dtype='int16')
            sess_recalled = np.zeros((n_lists, list_length), dtype='int8')
            sess_times = np.zeros((n_lists, recalls_allowed), dtype='int32')

            # Load presented and recalled words from that session's .lst and .par files, respectively
            for i in range(n_lists):
                try:
                    # print subj, sess_num, i
                    sess_pres_words[i, :] = np.loadtxt(os.path.join(session_dir, '%d.lst' % i), delimiter='\t', dtype='S32')
                    recs = np.loadtxt(os.path.join(session_dir, '%d.par' % i), delimiter='\t', dtype='S32')
                    recs = [w for w in np.atleast_2d(recs) if w[2] != 'VV'] if not recs.shape == (0,) else []
                except IOError:
                    bad_list_array[sess_num * 24 + i] = True
                    continue
                sess_rec_words[i, :len(recs)] = [w[2] for w in recs]
                sess_rec_nos[i, :len(recs)] = [w[1] for w in recs]
                sess_times[i, :len(recs)] = [int(w[0]) for w in recs]

            # Convert presented words to their ID numbers by referencing the full word pool (remember to add 1 to the IDs!)
            sess_pres_nos = np.searchsorted(wordpool, sess_pres_words) + 1

            # Determine whether each presented word was subsequently recalled, either in that trial or any later trial
            for i, row in enumerate(sess_pres_words):
                for j, w in enumerate(row):
                    if w in sess_rec_words[i:]:
                        sess_recalled[i, j] = 1

            # Create matrix with the serial positions of recalls
            sess_serialpos = make_serialpos_matrix(sess_pres_nos, sess_rec_nos)

            # Create matrix with intrusion info
            sess_intrusions = make_intrusions_matrix(sess_pres_nos, sess_rec_nos)

            # Place that session's behavioral data into the appropriate rows of the subject's full data matrices
            start_row = sess_num * n_lists
            end_row = start_row + n_lists
            mat_pairs = [(pres_words, sess_pres_words), (pres_nos, sess_pres_nos), (rec_words, sess_rec_words),
                         (rec_nos, sess_rec_nos), (recalled, sess_recalled), (times, sess_times),
                         (serialpos, sess_serialpos), (intrusions, sess_intrusions)]
            for pair in mat_pairs:
                pair[0][start_row:end_row, :] = pair[1]

        # Identify the max number of recalls the subject made on any trial of any session, as this is the number of
        # columns we should keep in our recall-related matrices
        max_recalls = np.where(rec_nos != 0)[1].max() + 1

        # Trim unused columns of the recall-related data matrices
        rec_words = rec_words[:, :max_recalls]
        rec_nos = rec_nos[:, :max_recalls]
        times = times[:, :max_recalls]
        serialpos = serialpos[:, :max_recalls]
        intrusions = intrusions[:, :max_recalls]

        # Once all of a subject's data has been processed, add their completed data matrices to the data dictionary
        data[subj] = dict(
            subject=subj_array.tolist(),
            session=sess_array.tolist(),
            bad_list=bad_list_array.tolist(),

            pres_words=pres_words.tolist(),
            pres_nos=pres_nos.tolist(),
            rec_words=rec_words.tolist(),
            rec_nos=rec_nos.tolist(),
            times=times.tolist(),
            serialpos=serialpos.tolist(),
            intrusions=intrusions.tolist()
        )

        with open(outfile, 'w') as f:
            json.dump(data[subj], f)


if __name__ == "__main__":
    make_data_matrices_ltpFR2()
