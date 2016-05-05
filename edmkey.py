#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

import os
from time import clock
from fodules.key import *
from fodules.folder import make_unique_dir
from argparse import ArgumentParser

clock()
parser = ArgumentParser(description="key estimation algorithm")
parser.add_argument("input",
                    help="file or dir to analyse")
parser.add_argument("-x", "--xtra",
                    action="store_true",
                    help="extra analysis (with modal details)")
parser.add_argument("-v", "--verbose",
                    action="store_true",
                    help="print estimations to console")
parser.add_argument("-o", "--overwrite",
                    action="store_true",
                    help="overwrite existing subdir if exists.")
parser.add_argument("-w", "--write_to",
                    help="specify dir to export results")
args = parser.parse_args()

if args.write_to:
    if not os.path.isdir(args.write_to):
        raise parser.error("'{0}' is not a valid directory for writing.".format(args.input))
    else:
        output_dir = args.write_to
else:
    output_dir = args.input
print "Creating subfolder with results in '{0}'.".format(output_dir)

# if args.file:
#     if not os.path.isfile(args.input):
#         raise parser.error("'{0}' is not a valid file.".format(args.input))
#     else:
#         output_dir = make_unique_dir(output_dir)
#         r = key_estimate_extended(args.input, output_dir)
#         if args.verbose:
#             print args.input, '-', r
# else:
if not os.path.isdir(args.input):
    raise parser.error("'{0}' is not a directory.".format(args.input))
else:
    analysis_folder = args.input[1 + args.input.rfind('/'):]
    output_dir = make_unique_dir(output_dir, tag=analysis_folder)
    conf_file = open('conf.py', 'r')
    write_conf_to = open(output_dir + '/conf.txt', 'w')
    write_conf_to.write(conf_file.read())
    write_conf_to.close()
    conf_file.close()
    list_all_files = os.listdir(args.input)
    print 'Analysing files...'
    count_files = 0
    if args.xtra:
        print "You have selected extra analysis features. This might take a while."
    else:
        print "Simple analysis."
    for item in list_all_files:
        if any(soundfile_type in item for soundfile_type in AUDIO_FILE_TYPES):
            audiofile = args.input + '/' + item
            if args.xtra:
                estimation = key_estimate_extended(audiofile, output_dir)
            else:
                estimation = key_estimate(audiofile, output_dir)
            if args.verbose:
                print "{0} - {1}".format(audiofile, estimation)
            count_files += 1
    print "{0} audio files analysed in {1} seconds.".format(count_files, clock())
