#!/usr/local/bin/python
#  -*- coding: UTF-8 -*-

import sys
import librosa
import librosa.display
import essentia.standard as estd
import essentia

from pcp import *
from fileutils import *
from settings_librosa import *


def get_key(input_audio_file, output_text_file):
    """
    This function estimates the overall key of an audio track
    optionaly with extra modal information.
    :type input_audio_file: str
    :type output_text_file: str
    """
    if USE_THREE_PROFILES:
        key_1 = estd.KeyEDM3(pcpSize=HPCP_SIZE, profileType=KEY_PROFILE)
    else:
        key_1 = estd.KeyEDM(pcpSize=HPCP_SIZE, profileType=KEY_PROFILE)
    if WITH_MODAL_DETAILS:
        key_2 = estd.KeyExtended(pcpSize=HPCP_SIZE)
    audio, sr = librosa.load(path=input_audio_file,
                             sr=SAMPLE_RATE,
                             duration=FIRST_N_SECS_ONLY,
                             offset=SKIP_N_SECS_AT_START)

    chroma = librosa.feature.chroma_cqt(y=audio, sr=SAMPLE_RATE)
    chroma = chroma.transpose()
    chroma = np.sum(chroma, axis=0)
    chroma = normalize_pcp_peak(chroma)
    chroma = np.roll(chroma, 3)
    if PCP_THRESHOLD is not None:
        chroma = pcp_gate(chroma, PCP_THRESHOLD)
    if DETUNING_CORRECTION:
        chroma = shift_pcp(chroma, HPCP_SIZE)
    chroma = essentia.array(chroma)
    estimation_1 = key_1(chroma)
    key_1 = estimation_1[0] + '\t' + estimation_1[1]
    if WITH_MODAL_DETAILS:
        estimation_2 = key_2(chroma)
        key_2 = estimation_2[0] + '\t' + estimation_2[1]
    if WITH_MODAL_DETAILS:
        key_verbose = key_1 + '\t' + key_2
        key = key_verbose.split('\t')
        if key[3] == 'monotonic' and key[0] == key[2]:
            key = '{0}\tminor'.format(key[0])
        else:
            key = key_1
    else:
        key = key_1
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
    parser.add_argument("-x", "--extra",
                        action="store_true",
                        help="generate extra analysis files")
    parser.add_argument("-c", "--conf_file",
                        help="specify a different configuration file")
    args = parser.parse_args()

    if not args.batch_mode:
        if not os.path.isfile(args.input):
            print("\nWARNING:")
            print("Could not find {0}".format(args.input))
            print("Are you sure is it a valid filename?\n")
            sys.exit()
        elif os.path.isfile(args.input):
            print("\nAnalysing:\t{0}".format(args.input))
            print("Exporting to:\t{0}.".format(args.output))
            estimation = get_key(args.input, args.output)
            if args.verbose:
                print(":\t{0}".format(estimation)),
        else:
            raise IOError("Unknown ERROR in single file mode")
    else:
        if os.path.isdir(args.input):
            analysis_folder = args.input[1 + args.input.rfind('/'):]
            if os.path.isfile(args.output):
                print("\nWARNING:")
                print("It seems that you are trying to replace an existing file")
                print("In batch_mode, the output argument must be a directory".format(args.output))
                print("Type 'fkey -h' for help\n")
                sys.exit()
            output_dir = results_directory(args.output)
            list_all_files = os.listdir(args.input)
            print("\nAnalysing audio files in:\t{0}".format(args.input))
            print("Writing results to:\t{0}\n".format(args.output))
            count_files = 0
            for a_file in list_all_files:
                if any(soundfile_type in a_file for soundfile_type in VALID_FILE_TYPES):
                    input_file = args.input + '/' + a_file
                    output_file = args.output + '/' + a_file[:-4] + '.txt'
                    estimation = get_key(input_file, output_file)
                    if args.verbose:
                        print("{0} - {1}".format(input_file, estimation))
                    count_files += 1
            print("{0} audio files analysed".format(count_files, clock()))
        else:
            raise IOError("Unknown ERROR in batch mode")
    print("Finished in:\t{0} secs.\n".format(clock()))
