#!/usr/local/bin/python
#  -*- coding: UTF-8 -*-

import os
from numpy import divide as npdivide
from numpy import mean as npmean


def name_to_class(key):
    """
    Converts a note name to its pitch-class value.
    :type key: str
    """
    name2class = {'B#': 0,  'C':  0,
                  'C#': 1,  'Db': 1,
                  'D':  2,
                  'D#': 3,  'Eb': 3,
                  'E':  4,  'Fb': 4,
                  'E#': 5,  'F':  5,
                  'F#': 6,  'Gb': 6,
                  'G':  7,
                  'G#': 8,  'Ab': 8,
                  'A':  9,  'A#': 10,
                  'Bb': 10, 'B':  11,
                  'Cb': 11,
                  '??': 12, '-':  12}
    return name2class[key]


def mode_to_num(mode):
    """
    Converts a scale type into numeric values (maj = 0, min = 1).
    :type mode: str
    """
    mode2num = {'major': 0,
                'minor': 1}
    return mode2num[mode]


def key_to_list(key):
    """
    Converts a key (i.e. C major) type into a
    numeric list in the form [tonic, mode].
    :type key: str
    """
    key = key.split('\t')
    key[-1] = key[-1].strip()
    if len(key) == 1:
        key = [name_to_class(key[0]), 0]
    else:
        key = [name_to_class(key[0]), mode_to_num(key[1])]
    return key


def mirex_score(estimation, truth):
    """
    Performs an evaluation of the key estimation
    according to the MIREX score, assigning
    - 1.0 points to correctly identified keys,
    - 0.5 points to keys at a distance of a perfect fifth,
    - 0.3 points to relative keys,
    - 0.2 points to parallel keys, and
    - 0.0 points to other types of errors.
    :param estimation: list with numeric values for key and mode :type str
    :param truth: list with numeric values for key and mode :type str
    """
    if estimation[0] == truth[0] and estimation[1] == truth[1]:
        points = 1.0
    elif estimation[0] == truth[0] and estimation[1] + truth[1] == 1:
        points = 0.2
    elif estimation[0] == (truth[0] + 7) % 12:
        points = 0.5
    elif estimation[0] == (truth[0] + 5) % 12:
        points = 0.5
    elif estimation[0] == (truth[0] + 3) % 12 and estimation[1] == 0 and truth[1] == 1:
        points = 0.3
    elif estimation[0] == (truth[0] - 3) % 12 and estimation[1] == 1 and truth[1] == 0:
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
        results = list(npdivide(results, size))
        results.append(npmean(list_with_weighted_results))
        return results


if __name__ == "__main__":

    from argparse import ArgumentParser

    parser = ArgumentParser(description="Print MIREX evaluation results to terminal.")
    parser.add_argument("annotations",
                        help="dir with groundtruth key annotations.")
    parser.add_argument("estimations",
                        help="dir with estimated keys.")
    args = parser.parse_args()

    if not os.path.isdir(args.estimations) and not os.path.isdir(args.annotations):
        raise parser.error("Warning: '{0}' or '{1}' not a directory.".format(args.annotations,
                                                                             args.estimations))
    else:
        results_mirex = []
        estimation_files = os.listdir(args.estimations)
        for element in estimation_files:
            if element[-4:] == ".txt":
                est_file = open(args.estimations + '/' + element, 'r')
                est_string = est_file.readline()
                est = key_to_list(est_string)
                est_file.close()
                try:
                    ann_file = open(args.annotations + '/' + element[:-4] + '.key', 'r')
                    ann_key = ann_file.readline()
                    ann_key = ann_key.split(' ')
                    ann_key = ann_key[0] + '\t' + ann_key[1]
                    ann = key_to_list(ann_key)
                    ann_file.close()
                except StandardError:
                    print "Didn't find annotation for current estimation. Skipping...\n"
                    continue
                score_mirex = mirex_score(est, ann)
                results_mirex.append(score_mirex)
        mirex_results = mirex_evaluation(results_mirex)
        print "\nMIREX RESULTS:"
        print "%.3f Correct" % mirex_results[0]
        print "%.3f Fifth error" % mirex_results[1]
        print "%.3f Relative error" % mirex_results[2]
        print "%.3f Parallel error" % mirex_results[3]
        print "%.3f Other errors" % mirex_results[4]
        print "%.3f Weighted score" % mirex_results[5]
