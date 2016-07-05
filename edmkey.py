#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

"""
import sys
import os
currentFolderPath = os.path.abspath(os.path.join(__file__, os.path.pardir))
sys.path.insert(1, os.path.join(currentFolderPath, "site-packages"))
print sys.path
"""

from time import clock
from fodules.key import *
from fodules.folder import make_unique_dir
from argparse import ArgumentParser

clock()
conf_file = open('./conf.py', 'r')
parser = ArgumentParser(description="Key Estimation Algorithm")
parser.add_argument("input",
                    help="file or dir to analyse")
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
elif os.path.isfile(args.input):
    output_dir = args.input[:args.input.rfind('/')]
elif os.path.isdir(args.input):
    output_dir = args.input

if os.path.isfile(args.input):
    analysis_file = args.input[1 + args.input.rfind('/'):]
    output_dir = make_unique_dir(output_dir, tag=analysis_file)
    print "Writing results to '{0}'.".format(output_dir)
    print 'Analysing {0}'.format(analysis_file),
    estimation = estimate_key(args.input, output_dir)
    if args.verbose:
        print ": {0}".format(estimation),
    print "({0} s.)".format(clock())

elif os.path.isdir(args.input):
    analysis_folder = args.input[1 + args.input.rfind('/'):]
    output_dir = make_unique_dir(output_dir, tag=analysis_folder)
    list_all_files = os.listdir(args.input)
    print 'Analysing files...'
    count_files = 0
    for item in list_all_files:
        if any(soundfile_type in item for soundfile_type in VALID_FILE_TYPES):
            audiofile = args.input + '/' + item
            estimation = estimate_key(audiofile, output_dir)
            if args.verbose:
                print "{0} - {1}".format(audiofile, estimation)
            count_files += 1
    print "{0} audio files analysed in {1} secs.".format(count_files, clock())
else:
    raise parser.error("'{0}' is not a valid argument.".format(args.input))

write_conf_to = open(output_dir + '/conf.txt', 'w')
write_conf_to.write(conf_file.read())
write_conf_to.close()
conf_file.close()
