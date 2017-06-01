#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

import os


def append_groundtruth(dir_estimations, dir_annotations):
    e = os.listdir(dir_estimations)
    for item in e:
        if '.key' in item:
            print item
            a = open(dir_annotations + '/' + item, 'r')
            l = a.readline()
            a.close()
            f = open(dir_estimations + '/' + item, 'a')
            f.write('\t' + l)
            f.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Appends the ground-truth annotations \ "
                                                 "to a file with estimations.")
    parser.add_argument("estimations", help="dir with estimations")
    parser.add_argument("annotations", help="dir with ground-truth annotations")
    args = parser.parse_args()

    print "Processing files..."
    append_groundtruth(args.estimations, args.annotations)
    print 'Done!'
