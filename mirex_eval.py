#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

import os
import numpy as np
import xlrd
import xlwt
import csv
from fodules.label import key_to_int


def mirex_score(est, truth):
    """
    Performs an evaluation of the key estimation
    according to the MIREX score, assigning
    - 1.0 points to correctly identified keys,
    - 0.5 points to keys at a distance of a perfect fifth,
    - 0.3 points to relative keys,
    - 0.2 points to parallel keys, and
    - 0.0 points to other types of errors.
    :param est: list with numeric values for key and mode :type str
    :param truth: list with numeric values for key and mode :type str
    """
    if est[0] == truth[0] and est[1] == truth[1]:
        points = 1.0
    elif est[0] == truth[0] and est[1] + truth[1] == 1:
        points = 0.2
    elif est[0] == (truth[0] + 7) % 12:
        points = 0.5
    elif est[0] == (truth[0] + 5) % 12:
        points = 0.5
    elif est[0] == (truth[0] + 3) % 12 and est[1] == 0 and truth[1] == 1:
        points = 0.3
    elif est[0] == (truth[0] - 3) % 12 and est[1] == 1 and truth[1] == 0:
        points = 0.3
    else:
        points = 0.0
    return points


def mirex_evaluation(list_with_weighted_results):
    """
    This function expects a list with all the weighted results
    according to the MIREX competition, returning a list with the
    results for each of these categories plus a weighted score.
    :type list_with_weighted_results: list
    """
    results = 5 * [0]
    size = float(len(list_with_weighted_results))
    if size == 0:
        raise ZeroDivisionError("Did not find any results to evaluate!")
    else:
        for f in list_with_weighted_results:
            if f == 1:
                results[0] += 1.0
            elif f == 0.5:
                results[1] += 1.0
            elif f == 0.3:
                results[2] += 1.0
            elif f == 0.2:
                results[3] += 1.0
            elif f == 0:
                results[4] += 1.0
        results = list(np.divide(results, size))
        results.append(np.mean(list_with_weighted_results))
        return results


def error_type(est, truth):
    """
    Performs a detailed evaluation of the key estimation.
    :type est: list with numeric values for key and mode
    :type truth: list with numeric values for key and mode
    """
    pc2degree = {0: 'I',
                 1: 'bII',
                 2: 'II',
                 3: 'bIII',
                 4: 'III',
                 5: 'IV',
                 6: '#IV',
                 7: 'V',
                 8: 'bVI',
                 9: 'VI',
                 10: 'bVII',
                 11: 'VII'}
    interval = (est[0] - truth[0]) % 12
    degree = pc2degree[interval]
    error_id = 2 * (interval + (est[1] * 12)) + truth[1]
    if est[1] == 1:
        degree = degree.lower()
    else:
        degree = degree.upper()
        degree = degree.replace('B', 'b')
    if truth[1] == 1:
        degree = 'i as ' + degree
    else:
        degree = 'I as ' + degree
    return error_id, degree


def xls_to_key_annotations(excel_file, sheet_index, export_directory):

    excel_file = xlrd.open_workbook(excel_file)
    spreadsheet = excel_file.sheet_by_index(sheet_index)

    for row in range(spreadsheet.nrows):
        v = spreadsheet.row_values(row)
        txt = open(export_directory + '/' + v[0] + '.key', 'w')
        if len(v[1]) > 3:
            txt.write(v[1] + '\n')
        else:
            txt.write(v[1] + ' major\n')
        txt.close()


def matrix_to_excel(my_matrix,
                    label_rows=('C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'),
                    label_cols=('C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'),
                    filename='matrix.xls'):

    wb = xlwt.Workbook()
    ws = wb.add_sheet('Sheet1')

    start_row = 1
    for label in label_rows:
        ws.write(start_row, 0, label)
        start_row += 1

    start_col = 1
    for label in label_cols:
        ws.write(0, start_col, label)
        start_col += 1

    next_row = 1
    next_col = 1
    for row in my_matrix:
        col = next_col
        for item in row:
            ws.write(next_row, col, item)
            col += 1
        next_row += 1

    wb.save(filename)


def features_from_csv(csv_file, start_col=0, end_col=1):
    saved_values = []
    csv_file = open(csv_file, 'r')
    csv_file = csv.reader(csv_file, skipinitialspace=True)
    for row in csv_file:
        saved_values.append(map(float, row[start_col:end_col]))
    return np.array(saved_values)


def stringcell_from_csv(csv_file, col=27):
    saved_values = []
    csv_file = open(csv_file, 'r')
    csv_file = csv.reader(csv_file, skipinitialspace=True)
    for row in csv_file:
        saved_values.append(row[col])
    return np.array(saved_values)


def keycell_from_csv(csv_file, col=27):
    saved_values = []
    csv_file = open(csv_file, 'r')
    csv_file = csv.reader(csv_file, skipinitialspace=True)
    for row in csv_file:
        saved_values.append(key_to_int(row[col]))
    return np.array(saved_values)


def key_to_int(key):
    """
    Converts a key symbol (i.e. C major) type to int
    :type key: str
    """
    name2class = {'C major': 0,
                  'C# major': 1, 'Db major': 1,
                  'D major': 2,
                  'D# major': 3, 'Eb major': 3,
                  'E major': 4,
                  'F major': 5,
                  'F# major': 6, 'Gb major': 6,
                  'G major': 7,
                  'G# major': 8, 'Ab major': 8,
                  'A major': 9,
                  'A# major': 10, 'Bb major': 10,
                  'B major': 11,

                  'C minor': 12,
                  'C# minor': 13, 'Db minor': 13,
                  'D minor': 14,
                  'D# minor': 15, 'Eb minor': 15,
                  'E minor': 16,
                  'F minor': 17,
                  'F# minor': 18, 'Gb minor': 18,
                  'G minor': 19,
                  'G# minor': 20, 'Ab minor': 20,
                  'A minor': 21,
                  'A# minor': 22, 'Bb minor': 22,
                  'B minor': 23,
                  }
    return name2class[key]


def int_to_key(a_number):
    """
    Converts an int onto a key symbol with root and scale.
    :type a_number: int
    """
    int2key    = {0:  'C major',
                  1:  'C# major',
                  2:  'D major',
                  3:  'Eb major',
                  4:  'E major',
                  5:  'F major',
                  6:  'F# major',
                  7:  'G major',
                  8:  'Ab major',
                  9:  'A major',
                  10: 'Bb major',
                  11: 'B major',

                  12: 'C minor',
                  13: 'C# minor',
                  14: 'D minor',
                  15: 'Eb minor',
                  16: 'E minor',
                  17: 'F minor',
                  18: 'F# minor',
                  19: 'G minor',
                  20: 'Ab minor',
                  21: 'A minor',
                  22: 'Bb minor',
                  23: 'B minor',
                  }
    return int2key[a_number]


if __name__ == "__main__":

    from argparse import ArgumentParser

    parser = ArgumentParser(description="Perform MIREX evaluation and print results to terminal")
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
