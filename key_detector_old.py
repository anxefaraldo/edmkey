#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

"""This script estimates the key of the songs contained in a folder,
and performs an evaluation of its results according to the MIREX
standard.
There are two modes of operation: 'txt' and 'title'.
In 'txt mode, the program expects a first argument indicating the route
to a folder containing the audio to be analysed, and a second argument
containing the route to the ground truth annotation as individual text
files. The program expects that the file names of both the audio and the
annotations are equal (except for the extension), and if the name do not
match it will skip the evaluation for that file.
In 'title' mode, the program looks for the ground-truth annotation embedded
in the name of the audio file itself, according to the following format:

FORMAT:  'Artist Name - Title of the Song = Key annotation < genre > DATASET.wav'
EXAMPLE: 'Audio Junkies - Bird On A Wire = F minor < edm > KF1000.wav'

Besides common python libraries, this script depends on a module named
"keytools" which is provided along this file.

                                              Ángel Faraldo, March 2015."""


# LOAD MODULES
# ============
import sys
import os
import numpy as np
import essentia.standard as estd


def results_directory(out_dir):
    """
    creates a sub-folder in the specified directory
    with some of the algorithm parameters.
    :type out_dir: str
    """
    if not os.path.isdir(out_dir):
        print "CREATING DIRECTORY '{0}'.".format(out_dir)
        if not os.path.isabs(out_dir):
            raise IOError("Not a valid path name.")
        else:
            os.mkdir(out_dir)
    return out_dir


def shift_pcp(pcp, pcp_size=12):
    """
    Shifts a pcp to the nearest tempered bin.
    :type pcp: list
    :type pcp_size: int
    """
    tuning_resolution = pcp_size / 12
    max_val = np.max(pcp)
    if max_val <= [0]:
        max_val = [1]
    pcp = np.divide(pcp, max_val)
    max_val_index = np.where(pcp == 1)
    max_val_index = max_val_index[0][0] % tuning_resolution
    if max_val_index > (tuning_resolution / 2):
        shift_distance = tuning_resolution - max_val_index
    else:
        shift_distance = max_val_index
    pcp = np.roll(pcp, shift_distance)
    return pcp


# WHAT TO ANALYSE
# ===============
analysis_mode = 'txt'  # {'txt', 'title'}
# I should find a standardized way of analysing... I like the fact that we can
# analyse per collection, based on the criteria below, and also that everything
# is kept on the same folder...


# ANALYSIS PARAMETERS
# ===================
# faraldo:
avoid_edges          = 0  # % of duration at the beginning and end that is not analysed.
first_n_secs         = 30  # only analyse the first N seconds of each track (o = full track)
skip_first_minute    = False
spectral_whitening   = True
shift_spectrum       = True
shift_scope          = 'average'  # ['average', 'frame']

# print and VERBOSE:
verbose              = True
confusion_matrix     = True
results_to_file      = True
results_to_csv       = True
confidence_threshold = 1
# global:
sample_rate          = 44100
window_size          = 4096
jump_frames          = 1  # 1 = analyse every frame; 2 = analyse every other frame; etc.
random_frames        = [1, 5]  # range of random generator for analysing frames...
hop_size             = window_size * jump_frames
window_type          = 'hann'
min_frequency        = 25
max_frequency        = 3500
# spectral peaks:
magnitude_threshold  = 0.0001
max_peaks            = 60
# hpcp:
band_preset          = False
split_frequency      = 250  # if band_preset == True
harmonics            = 4
non_linear           = True
normalize            = True
reference_frequency  = 440
hpcp_size            = 36
weight_type          = "squaredCosine"  # {none, cosine or squaredCosine}
weight_window_size   = 1  # semitones
# key detector:
profile_type         = 'bmtg3'
use_three_chords     = False  # BEWARE: False executes the extra code including all triads!
use_polyphony        = False
num_harmonics        = 15   # when use_polyphony == True
slope                = 0.2  # when use_polyphony == True
VALID_FILE_TYPES             = {'.wav', '.mp3', 'flac', '.aiff', '.ogg'}

# ////////////////////////////////////////////////////////////////////////////


def estimate_key(input_audio_file, output_text_file):
    loader = estd.MonoLoader(filename=input_audio_file,
                             sampleRate=sample_rate)
    cut = estd.FrameCutter(frameSize=window_size,
                           hopSize=hop_size)
    window = estd.Windowing(size=window_size,
                            type=window_type)
    rfft = estd.Spectrum(size=window_size)
    sw = estd.SpectralWhitening(maxFrequency=max_frequency,
                                sampleRate=sample_rate)
    speaks = estd.SpectralPeaks(magnitudeThreshold=magnitude_threshold,
                                maxFrequency=max_frequency,
                                minFrequency=min_frequency,
                                maxPeaks=max_peaks,
                                sampleRate=sample_rate)
    hpcp = estd.HPCP(bandPreset=band_preset,
                     harmonics=harmonics,
                     maxFrequency=max_frequency,
                     minFrequency=min_frequency,
                     nonLinear=non_linear,
                     normalized=normalize,
                     referenceFrequency=reference_frequency,
                     sampleRate=sample_rate,
                     size=hpcp_size,
                     splitFrequency=split_frequency,
                     weightType=weight_type,
                     windowSize=weight_window_size)
#    key = estd.Key(numHarmonics=num_harmonics,
    #              pcpSize=hpcp_size,
    #              profileType=profile_type,
    #              slope=slope,
    #              usePolyphony=use_polyphony,
    #              useThreeChords=use_three_chords)
    key = estd.KeyEDM3(pcpSize=hpcp_size,
                       profileType=profile_type)
    audio = loader()
    duration = len(audio)
    if skip_first_minute and duration > (sample_rate * 60):
        audio = audio[sample_rate * 60:]
        duration = len(audio)
    if first_n_secs > 0:
        if duration > (first_n_secs * sample_rate):
            audio = audio[:first_n_secs * sample_rate]
            duration = len(audio)
    if avoid_edges > 0:
        initial_sample = (avoid_edges * duration) / 100
        final_sample = duration - initial_sample
        audio = audio[initial_sample:final_sample]
        duration = len(audio)
    number_of_frames = duration / hop_size
    chroma = []
    for bang in range(number_of_frames):
        spek = rfft(window(cut(audio)))
        p1, p2 = speaks(spek)  # p1 are frequencies; p2 magnitudes
        if spectral_whitening:
            p2 = sw(spek, p1, p2)
        vector = hpcp(p1, p2)
        sum_vector = np.sum(vector)
        if sum_vector > 0:
            if shift_spectrum == False or shift_scope == 'average':
                chroma.append(vector)
            elif shift_spectrum and shift_scope == 'frame':
                vector = shift_pcp(vector, hpcp_size)
                chroma.append(vector)
            else:
                print "SHIFT_SCOPE must be set to 'frame' or 'average'"
    chroma = np.mean(chroma, axis=0)
    if shift_spectrum and shift_scope == 'average':
        chroma = shift_pcp(chroma, hpcp_size)
    key = key(chroma.tolist())
    key = key[0] + '\t' + key[1]
    textfile = open(output_text_file, 'w')
    textfile.write(key + '\n')
    textfile.close()
    return key


if __name__ == "__main__":

    from time import clock
    from argparse import ArgumentParser

    clock()
    parser = ArgumentParser(description="Key Estimation Algorithm")
    parser.add_argument("input",
                        help="file (dir if in --batch_mode) to analyse")
    parser.add_argument("output",
                        help="file (dir if in --batch_mode) to write results to")
    parser.add_argument("-b", "--batch_mode",
                        action="store_true",
                        help="batch analyse a whole directory")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="print progress to console")
    args = parser.parse_args()

    if not args.batch_mode:
        if not os.path.isfile(args.input):
            print "\nWARNING:"
            print "Could not find {0}".format(args.input)
            print "Are you sure is it a valid filename?\n"
            sys.exit()
        elif os.path.isfile(args.input):
            print "\nAnalysing:\t{0}".format(args.input)
            print "Exporting to:\t{0}.".format(args.output)
            estimation = estimate_key(args.input, args.output)
            if args.verbose:
                print ":\t{0}".format(estimation),
        else:
            raise IOError("Unknown ERROR in single file mode")
    else:
        if os.path.isdir(args.input):
            analysis_folder = args.input[1 + args.input.rfind('/'):]
            if os.path.isfile(args.output):
                print "\nWARNING:"
                print "It seems that you are trying to write onto an existing file"
                print "In batch_mode, the output argument must be a directory".format(args.output)
                print "Type 'FkeyEDM -h' for help\n"
                sys.exit()
            output_dir = results_directory(args.output)
            list_all_files = os.listdir(args.input)
            print "\nAnalysing audio files in:\t{0}".format(args.input)
            print "Writing estimation files to:\t{0}\n".format(args.output)
            count_files = 0
            for a_file in list_all_files:
                if any(soundfile_type in a_file for soundfile_type in VALID_FILE_TYPES):
                    input_file = args.input + '/' + a_file
                    output_file = args.output + '/' + a_file[:-4] + '.txt'
                    estimation = estimate_key(input_file, output_file)
                    if args.verbose:
                        print "{0} - {1}".format(input_file, estimation)
                    count_files += 1
            print "{0} audio files analysed".format(count_files, clock())
        else:
            raise IOError("Unknown ERROR in batch mode")
    print "Finished in:\t{0} secs.\n".format(clock())
