#!/usr/local/bin/python
#  -*- coding: UTF-8 -*-

import sys
import librosa
import librosa.display
import matplotlib.pyplot as plt

import numpy as np
import scipy.stats

import essentia.standard as estd
import essentia

from pcp import *
from fileutils import *
from settings import *


def get_key(input_audio_file, output_text_file):
    """
    This function estimates the overall key of an audio track
    optionaly with extra modal information.
    :type input_audio_file: str
    :type output_text_file: str
    """
    # I am going to try tro get rid of essentia's modules... especially those prone to have errors...
    # I mostly will use librosa to this purpose
    ##### loader = estd.MonoLoader(filename=input_audio_file,
    #####                          sampleRate=SAMPLE_RATE)
    cut = estd.FrameCutter(frameSize=WINDOW_SIZE,
                           hopSize=HOP_SIZE)
    window = estd.Windowing(size=WINDOW_SIZE,
                            type=WINDOW_SHAPE,
                            zeroPhase=False)
    # In particular the fft part will be rewritten...
    rfft = estd.Spectrum(size=WINDOW_SIZE)
    sw = estd.SpectralWhitening(maxFrequency=MAX_HZ,
                                sampleRate=SAMPLE_RATE)
    speaks = estd.SpectralPeaks(magnitudeThreshold=SPECTRAL_PEAKS_THRESHOLD,
                                maxFrequency=MAX_HZ,
                                minFrequency=MIN_HZ,
                                maxPeaks=SPECTRAL_PEAKS_MAX,
                                sampleRate=SAMPLE_RATE)
    hpcp = estd.HPCP(bandPreset=HPCP_BAND_PRESET,
                     bandSplitFrequency=HPCP_SPLIT_HZ,
                     harmonics=HPCP_HARMONICS,
                     maxFrequency=MAX_HZ,
                     minFrequency=MIN_HZ,
                     nonLinear=HPCP_NON_LINEAR,
                     normalized=HPCP_NORMALIZE,
                     referenceFrequency=HPCP_REFERENCE_HZ,
                     sampleRate=SAMPLE_RATE,
                     size=HPCP_SIZE,
                     weightType=HPCP_WEIGHT_TYPE,
                     windowSize=HPCP_WEIGHT_WINDOW_SEMITONES,
                     maxShifted=HPCP_SHIFT)

    if USE_THREE_PROFILES:
        key_1 = estd.KeyEDM3(pcpSize=HPCP_SIZE, profileType=KEY_PROFILE)
    else:
        key_1 = estd.KeyEDM(pcpSize=HPCP_SIZE, profileType=KEY_PROFILE)
    if WITH_MODAL_DETAILS:
        key_2 = estd.KeyExtended(pcpSize=HPCP_SIZE)
    if HIGHPASS_CUTOFF == 0:
        ##### audio = loader()
        audio, sr = librosa.load(path=input_audio_file,
                                 sr=SAMPLE_RATE,
                                 mono=True,
                                 duration=FIRST_N_SECS_ONLY,
                                 offset=SKIP_N_SECS_AT_START)
    # else:
        ##### hpf = estd.HighPass(cutoffFrequency=HIGHPASS_CUTOFF, sampleRate=SAMPLE_RATE)
        #####audio = hpf(hpf(hpf(loader())))
        ##### audio, sr = librosa.load(path=input_audio_file, sr=SAMPLE_RATE, mono=True)
    #chroma_cqt = librosa.feature.chroma_cqt(y=audiol,
    #                                         sr=SAMPLE_RATE)
    #                                         C=None,
    #                                         hop_length=HOP_SIZE,
    #                                         # fmin=None,
    #                                         # norm=np.inf,
    #                                         # threshold=0.0,
    #                                         # tuning=None,
    #                                         n_chroma=12,
    #                                         n_octaves=7,
    #                                         # window=None,
    #                                         bins_per_octave=HPCP_SIZE)
    #                                         cqt_mode='full')
    duration = len(audio)
    ##### chroma = []
    #if AVOID_TIME_EDGES > 0:
    #    initial_sample = (AVOID_TIME_EDGES * duration) / 100
    #    final_sample = duration - initial_sample
    #    audio = audio[initial_sample:final_sample]
    #    duration = len(audio)
    n_slices = duration / HOP_SIZE
    chroma = np.empty([HPCP_SIZE * n_slices, 12], dtype='float32')
    for slice_n in range(n_slices):
        spek = rfft(window(cut(audio)))
        p1, p2 = speaks(spek)
        if SPECTRAL_WHITENING:
            p2 = sw(spek, p1, p2)
        pcp = hpcp(p1, p2)
        if np.sum(pcp) > 0:
            if not DETUNING_CORRECTION or DETUNING_CORRECTION_SCOPE == 'average':
                chroma[slice_n] = pcp
                # np.append(chroma, pcp)
            elif DETUNING_CORRECTION and DETUNING_CORRECTION_SCOPE == 'frame':
                pcp = shift_pcp(pcp, HPCP_SIZE)
                chroma[slice_n] = pcp
                ##### chroma.append(pcp)
            else:
                raise NameError("SHIFT_SCOPE must be set to 'frame' or 'average'.")
    if not chroma.any():
        return 'Silence\n'
    chroma = np.sum(chroma, axis=0)
    chroma = normalize_pcp_peak_np(chroma)
    if PCP_THRESHOLD != 0:
        chroma = pcp_gate(chroma, PCP_THRESHOLD)
    if DETUNING_CORRECTION and DETUNING_CORRECTION_SCOPE == 'average':
        chroma = shift_pcp(chroma, HPCP_SIZE) # before we had to convert 'chroma' to regular list.
    chroma = essentia.array(chroma) # we keed this to use essentia's Key estimator until we port ours to python
    estimation_1 = key_1(chroma)
    key_1 = estimation_1[0] + '\t' + estimation_1[1]
    if WITH_MODAL_DETAILS:
        estimation_2 = key_2(chroma)
        key_2 = estimation_2[0] + '\t' + estimation_2[1]
    if WITH_MODAL_DETAILS:
        key_verbose = key_1 + '\t' + key_2
        key = key_verbose.split('\t')
        # Assign amodal or difficult tracks to minor:
        if key[3] == 'monotonic' and key[0] == key[2]:
            key = '{0}\tminor'.format(key[0])
        # if key[3] == 'fifth' and key[0] == key[2]:
             # key = '{0}\tminor'.format(key[0])
        # if key[3] == 'difficult' and key[0] == key[2]:
        #    key = '{0}\tminor'.format(key[0])
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
