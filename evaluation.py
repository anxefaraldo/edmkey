#!/usr/local/bin/python
#  -*- coding: UTF-8 -*-

import os
from numpy import divide, mean, array, zeros


def matrix_to_excel(my_matrix,
                    label_rows=('C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'),
                    label_cols=('C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'),
                    filename='matrix.xls'):
    import xlwt

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
        for ii in row:
            ws.write(next_row, col, ii)
            col += 1
        next_row += 1

    wb.save(filename)


def merge_files(dir_with_files, new_filename):
    o = open(new_filename, 'w')
    e = os.listdir(dir_with_files)
    for item in e:
        if '.key' in item:
            f = open(dir_with_files + '/' + item, 'r')
            l = f.read()
            o.write(l + '\n')
            f.close()
    o.close()


def name_to_class(key):
    """
    Converts a note name to its pitch-class value.
    :type key: str
    """
    name2class = {'B#': 0, 'C': 0,
                  'C#': 1, 'Db': 1,
                  'D':  2,
                  'D#': 3, 'Eb': 3,
                  'E':  4, 'Fb': 4,
                  'E#': 5, 'F': 5,
                  'F#': 6, 'Gb': 6,
                  'G':  7,
                  'G#': 8, 'Ab': 8,
                  'A':  9, 'A#': 10,
                  'Bb': 10, 'B': 11,
                  'Cb': 11,
                  '??': 12, '-': 12}
    try:
        return name2class[key]
    except KeyError:
        print('name not defined in dictionary')


def mode_to_num(mode):
    """
    Converts a scale type into numeric values (maj = 0, min = 1).
    :type mode: str
    """
    mode2num = {'major':      0,
                'minor':      1,
                'maj':        0,
                'min':        1,
                'M':          0,
                'm':          1,
                '':           0,
                'ionian':     2,
                'harmonic':   3,
                'mixolydian': 4,
                'phrygian':   5,
                'fifth':      6,
                'monotonic':  7,
                'difficult':  8,
                'peak':       9,
                'flat':       10}
    try:
        return mode2num[mode]
    except KeyError:
        print('mode type not defined in dictionary')


def key_to_list(key):
    """
    Converts a key (i.e. C major) type into a
    numeric list in the form [tonic, mode].
    :type key: str
    """
    if len(key) <= 2:
        key = key.strip()
        key = [name_to_class(key), 0]
        return key
    elif '\t' in key[1:3]:
        key = key.split('\t')
    elif ' ' in key[1:3]:
        key = key.split(' ')
    key[-1] = key[-1].strip()
    key = [name_to_class(key[0]), mode_to_num(key[1])]
    return key


def mirex_score(estimation, groundtruth):
    """
    Performs an evaluation of the key estimation
    according to the MIREX score, assigning
    - 1.0 points to correctly identified keys,
    - 0.5 points to keys at a distance of a perfect fifth,
    - 0.3 points to relative keys,
    - 0.2 points to parallel keys, and
    - 0.0 points to other types of errors.
    :param estimation: list with numeric values for key and mode :type str
    :param groundtruth: list with numeric values for key and mode :type str
    """
    if estimation[0] == groundtruth[0] and estimation[1] == groundtruth[1]:
        points = 1.0
    elif estimation[0] == groundtruth[0] and estimation[1] + groundtruth[1] == 1:
        points = 0.2
    elif estimation[0] == (groundtruth[0] + 7) % 12:
        points = 0.5
    elif estimation[0] == (groundtruth[0] + 5) % 12:
        points = 0.5
    elif estimation[0] == (groundtruth[0] + 3) % 12 and estimation[1] == 0 and groundtruth[1] == 1:
        points = 0.3
    elif estimation[0] == (groundtruth[0] - 3) % 12 and estimation[1] == 1 and groundtruth[1] == 0:
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
        exit(ZeroDivisionError("Did not find any results to evaluate!"))
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
        results = list(divide(results, size))
        results.append(mean(list_with_weighted_results))
        return results


def error_detail(estimation, groundtruth):
    """
    Performs a detailed evaluation of the key estimation.
    :type estimation: list with numeric values for key and mode
    :type groundtruth: list with numeric values for key and mode
    """
    pc2degree = {0:  'I',
                 1:  'bII',
                 2:  'II',
                 3:  'bIII',
                 4:  'III',
                 5:  'IV',
                 6:  '#IV',
                 7:  'V',
                 8:  'bVI',
                 9:  'VI',
                 10: 'bVII',
                 11: 'VII'}
    interval = (estimation[0] - groundtruth[0]) % 12
    degree = pc2degree[interval]
    error_id = 2 * (interval + (estimation[1] * 12)) + groundtruth[1]
    if estimation[1] == 1:
        degree = degree.lower()
    else:
        degree = degree.upper()
        degree = degree.replace('B', 'b')
    if groundtruth[1] == 1:
        degree = 'i as ' + degree
    else:
        degree = 'I as ' + degree
    return error_id, degree


if __name__ == "__main__":

    from argparse import ArgumentParser

    parser = ArgumentParser(description="Evaluation algorithm for key estimation task.")
    parser.add_argument("annotations",
                        help="dir with ground-truth key annotations.")
    parser.add_argument("estimations",
                        help="dir with estimated keys.")
    parser.add_argument("-t" "--analysis_type",
                        help="type of analysis to perform ({'mirex', 'detailed'}.")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="print results to console")
    parser.add_argument("-w", "--write_results",
                        help="write the results to a textfile")

    args = parser.parse_args()

    if not os.path.isdir(args.estimations) and not os.path.isdir(args.annotations):
        raise parser.error("Warning: '{0}' or '{1}' not a directory.".format(args.annotations,
                                                                             args.estimations))
    else:
        keys_matrix = (2 * 12) * (2 * 12) * [0]
        error_matrix = array(zeros(24 * 2).reshape(24, 2), dtype=int)
        results_mirex = []
        results_errors = []
        estimation_files = os.listdir(args.estimations)
        for element in estimation_files:
            if element[-4:] == '.key' or element[-4:] == '.txt':
                est_file = open(args.estimations + '/' + element, 'r')
                est_string = est_file.readline()
                # TODO: reimplement detailed estimations... csv's
                # est_string = est_string.split(', ')
                est = key_to_list(est_string)
                est_file.close()
                try:
                    # we assume that file names of estimations and annotations are equal!
                    ann_file = open(args.annotations + '/' + element[:-4] + '.txt', 'r')
                except IOError:
                    try:
                        ann_file = open(args.annotations + '/' + element[:-4] + '.key', 'r')
                    except IOError:
                        print "Didn't find a matching annotation for the current estimation...\n"
                        continue
                ann_key = ann_file.readline()
                ann = key_to_list(ann_key)
                ann_file.close()
                score_mirex = mirex_score(est, ann)
                results_mirex.append(score_mirex)
                # FROM EVALUATION SIMPLE:
                # score_mirex = str(score_mirex)
                type_error = error_detail(est, ann)
                results_errors.append(type_error[0])
                type_error = type_error[1]
                if args.verbose:
                    print "{0} - {1} as {2}, {3} = {4}".format(element,
                                                               est,
                                                               ann,
                                                               type_error,
                                                               score_mirex)
                xpos = (ann[0] + (ann[0] * 24)) + (ann[1] * 24 * 12)
                ypos = ((est[0] - est[0]) + (est[1] * 12))
                keys_matrix[(xpos + ypos)] = + keys_matrix[(xpos + ypos)] + 1
        # GENERAL EVALUATION
        # ==================
        mirex_results = mirex_evaluation(results_mirex)
        keys_matrix = array(keys_matrix).reshape(2 * 12, 2 * 12)
        for item in results_errors:
            error_matrix[item / 2, item % 2] += 1

        # WRITE RESULTS TO FILE
        # =====================
        if args.write_results:
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

        # PRINT RESULTS
        # =============
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

            print "\nMIREX RESULTS:"
            print "%.3f Correct" % mirex_results[0]
            print "%.3f Fifth error" % mirex_results[1]
            print "%.3f Relative error" % mirex_results[2]
            print "%.3f Parallel error" % mirex_results[3]
            print "%.3f Other errors" % mirex_results[4]
            print "%.3f Weighted score" % mirex_results[5]

