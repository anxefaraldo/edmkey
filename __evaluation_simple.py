#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

import os
from fodules.label import *
from fodules.evaluate import *
from argparse import ArgumentParser


parser = ArgumentParser(description="Simple evaliation Algorithm")
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
            # assuming that Tonic Mode separated by a Space:
            est_string = est_file.readline()
            print est_string
            est_string = est_string.split(', ')
            print est_string
            est_key = est_string[-2]
            print est_key
            # est_confidence = est_string[2]
            est = key_to_list(est_key)
            est_file.close()
            try:
                ann_file = open(args.annotations + '/' + element, 'r')
                ann_key = ann_file.readline()
                # TODO: prevent annotation as tab/space separated!
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
