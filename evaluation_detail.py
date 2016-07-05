#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

import os
import argparse
from fodules.label import *
from fodules.evaluate import *
from futils.merge_files import merge_files
from fodules.excel import matrix_to_excel

parser = argparse.ArgumentParser(prog='evaluation_detail',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description='''
    Automatic Evaluation of Key Estimations
    =======================================
    This implementation relies on our own analysis format.
    We expect a single estimation file per audio track
    with comma-separated fields. Only the first two fields
    are mandatory:
    "filename, key, confidence, pcp1, pcp2, ..., pcpn, pk1, pk2, ..., peakn, ..."

    Ground truth annotations are expected as single files:
    "Tonic (space) mode"
    ''')
parser.add_argument("annotations",
                    help="dir with ground truth key annotations.")
parser.add_argument("estimations",
                    help="dir with estimated keys.")
parser.add_argument("-v", "--verbose",
                    action="store_true",
                    help="print results to console")
args = parser.parse_args()

if not os.path.isdir(args.estimations) and not os.path.isdir(args.annotations):
    raise parser.error("Warning: '{0}' or '{1}' not a directory.".format(args.annotations,
                                                                         args.estimations))
else:
    keys_matrix = (2 * 12) * (2 * 12) * [0]
    error_matrix = np.array(np.zeros(24 * 2).reshape(24, 2), dtype=int)
    results_mirex = []
    results_errors = []
    print "\nEvaluating..."
    estimation_files = os.listdir(args.estimations)
    for element in estimation_files:
        if element[-4:] == ".key":
            est_file = open(args.estimations + '/' + element, 'r')
            est_string = est_file.readline()
            # assuming that Tonic Mode separated by a Space:
            est_string = est_string.split(', ')
            est_key = est_string[1]
            est_confidence = est_string[2]
            est = key_to_list(est_key)
            est_file.close()
            try:
                ann_file = open(args.annotations + '/' + element, 'r')
                ann_key = ann_file.readline()
                # TODO: allow annotations separated by tab or space!
                ann = key_to_list(ann_key)
                ann_file.close()
            except StandardError:
                print "Didn't find annotation for current estimation. Skipping...\n"
                continue
            score_mirex = mirex_score(est, ann)
            results_mirex.append(score_mirex)
            score_mirex = str(score_mirex)
            type_error = error_type(est, ann)
            results_errors.append(type_error[0])
            type_error = type_error[1]
            output = "{0}, {1}, {2}, ".format(ann_key,
                                              type_error,
                                              score_mirex)
            append_results = open(args.estimations + '/' + element, 'a')
            append_results.write(output)
            append_results.close()
            if args.verbose:
                print "{0} - {1} as {2}, {3} = {4}".format(element,
                                                           est_key,
                                                           ann_key,
                                                           type_error,
                                                           score_mirex)
            xpos = (ann[0] + (ann[0] * 24)) + (ann[1] * 24 * 12)
            ypos = ((est[0] - est[0]) + (est[1] * 12))
            keys_matrix[(xpos + ypos)] = + keys_matrix[(xpos + ypos)] + 1
    # GENERAL EVALUATION
    # ==================
    mirex_results = mirex_evaluation(results_mirex)
    keys_matrix = np.array(keys_matrix).reshape(2 * 12, 2 * 12)
    for item in results_errors:
        error_matrix[item / 2, item % 2] += 1
    # WRITE RESULTS TO FILES
    # ======================
    write_score = open(args.estimations + '/mirex.txt', 'w')
    write_score.write("%.3f\tcorrect\n" % mirex_results[0])
    write_score.write("%.3f\tfifth errors\n" % mirex_results[1])
    write_score.write("%.3f\trelative errors\n" % mirex_results[2])
    write_score.write("%.3f\tparallel errors\n" % mirex_results[3])
    write_score.write("%.3f\tother errors\n" % mirex_results[4])
    write_score.write("%.3f\tweighted score\n" % mirex_results[5])
    write_score.close()
    matrix_to_excel(error_matrix,
                    label_rows=('I', 'bII', 'II', 'bIII', 'III', 'IV',
                                '#IV', 'V', 'bVI', 'VI', 'bVII', 'VII',
                                'i', 'bii', 'ii', 'biii', 'iii', 'iv',
                                '#iv', 'v', 'bvi', 'vi', 'bvii', 'vii'),
                    label_cols=('I', 'i'),
                    filename=args.estimations + '/errors.xls')
    matrix_to_excel(keys_matrix,
                    label_rows=('C', 'C#', 'D', 'Eb', 'E', 'F',
                                'F#', 'G', 'G#', 'A', 'Bb', 'B',
                                'Cm', 'C#m', 'Dm', 'Ebm', 'Em', 'Fm',
                                'F#m', 'Gm', 'G#m', 'Am', 'Bbm', 'Bm'),
                    label_cols=('C', 'C#', 'D', 'Eb', 'E', 'F',
                                'F#', 'G', 'G#', 'A', 'Bb', 'B',
                                'Cm', 'C#m', 'Dm', 'Ebm', 'Em', 'Fm',
                                'F#m', 'Gm', 'G#m', 'Am', 'Bbm', 'Bm'),
                    filename=args.estimations + '/confusion_matrix.xls')
    merge_files(args.estimations, args.estimations + '/merged_results.csv')

    if args.verbose:
        print '\nCONFUSION MATRIX:'
        print keys_matrix
        print "\nRELATIVE ERROR MATRIX:"
        row_label = ('I', 'bII', 'II', 'bIII', 'III', 'IV',
                     '#IV', 'V', 'bVI', 'VI', 'bVII', 'VII',
                     'i', 'bii', 'ii', 'biii', 'iii', 'iv',
                     '#iv', 'v', 'bvi', 'vi', 'bvii', 'vii')
        for i in range(len(error_matrix)):
            print row_label[i].rjust(4), error_matrix[i]
        print "\nMIREX EVALUATION:"
        print "%.3f Correct" % mirex_results[0]
        print "%.3f Fifth error" % mirex_results[1]
        print "%.3f Relative error" % mirex_results[2]
        print "%.3f Parallel error" % mirex_results[3]
        print "%.3f Other errors" % mirex_results[4]
        print "%.3f Weighted score" % mirex_results[5]
