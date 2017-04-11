#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

"""
import sys
import os
currentFolderPath = os.path.abspath(os.path.join(__file__, os.path.pardir))
sys.path.insert(1, os.path.join(currentFolderPath, "site-packages"))
print sys.path
"""

from argparse import ArgumentParser
from time import clock

from ML.train import *
from fodules.folder import make_unique_dir

clock()
conf_file = open('./settings.py', 'r')
parser = ArgumentParser(description="Key Estimation Algorithm")
parser.add_argument("input_data_folder",
                    help="dir with audio files to analyse")
parser.add_argument("ground_truth",
                    help="dir with ground-truth annotations.")
parser.add_argument("-v", "--verbose",
                    action="store_true",
                    help="print estimations to console")
parser.add_argument("-w", "--write_to",
                    help="specify dir to export results")
parser.add_argument("-c", "--conf_file",
                    help="specify a different configuration file")
args = parser.parse_args()

if args.write_to:
    if not os.path.isdir(args.write_to):
        raise parser.error("'{0}' is not a valid directory for writing.".format(args.input))
    else:
        output_dir = args.write_to
elif os.path.isdir(args.input_data_folder):
    output_dir = args.input_data_folder

if os.path.isdir(args.input_data_folder):
    analysis_folder = args.input_data_folder[1 + args.input_data_folder.rfind('/'):]
    output_dir = make_unique_dir(output_dir, tag=analysis_folder)
    write_conf_to = open(output_dir + '/conf.txt', 'w')
    write_conf_to.write(conf_file.read())
    write_conf_to.close()
    conf_file.close()
    analysis_files = os.listdir(args.input_data_folder)
    groundtruth_files = os.listdir(args.ground_truth)
    print 'Training...'
    count_files = 0
    for item in analysis_files:
        if any(soundfile_type in item for soundfile_type in VALID_FILE_TYPES):
            try:
                groundtruth_file = open(args.ground_truth + '/' + item[:-4] + '.key', 'r')
                groundtruth_key = groundtruth_file.readline()
                groundtruth_file.close()
                groundtruth = key_to_list(groundtruth_key)
            except StandardError:
                print "Didn't find groundtruth for current soundfile. Skipping...\n"
                continue
            audiofile = args.input_data_folder + '/' + item
            features, targets = get_features(audiofile, groundtruth)
            if args.verbose:
                print "{0} - {1}".format(targets, features)
            count_files += 1
    print "{0} audio files used for training in {1} secs.".format(count_files, clock())
else:
    raise parser.error("'{0}' is not a valid argument.".format(args.input_data_folder))
