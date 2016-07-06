#!/usr/local/bin/python
#  -*- coding: UTF-8 -*-

import os
import sys

currentFolderPath = os.path.abspath(os.path.join(__file__, os.path.pardir))
sys.path.insert(1, os.path.join(currentFolderPath, "site-packages"))

import numpy as np
import essentia.standard as estd
from collections import Counter

# ======================= #
# KEY ESTIMATION SETTINGS #
# ======================= #

# File Settings
# -------------
SAMPLE_RATE                  = 44100
VALID_FILE_TYPES             = {'.wav', '.mp3', 'flac', '.aiff', '.ogg'}

# Analysis Parameters
# -------------------
HIGHPASS_CUTOFF              = 200
SPECTRAL_WHITENING           = True
DETUNING_CORRECTION          = True
DETUNING_CORRECTION_SCOPE    = 'average'  # {'average', 'frame'}
PCP_THRESHOLD                = 0.66
WINDOW_SIZE                  = 4096
HOP_SIZE                     = 4096
WINDOW_SHAPE                 = 'hann'
MIN_HZ                       = 25
MAX_HZ                       = 3500
SPECTRAL_PEAKS_THRESHOLD     = 0.0001
SPECTRAL_PEAKS_MAX           = 60
HPCP_BAND_PRESET             = False
HPCP_SPLIT_HZ                = 250       # if HPCP_BAND_PRESET is True
HPCP_HARMONICS               = 4
HPCP_NON_LINEAR              = True
HPCP_NORMALIZE               = True
HPCP_SHIFT                   = False
HPCP_REFERENCE_HZ            = 440
HPCP_SIZE                    = 36
HPCP_WEIGHT_WINDOW_SEMITONES = 1         # semitones
HPCP_WEIGHT_TYPE             = 'cosine'  # {'none', 'cosine', 'squaredCosine'}

# Scope and Key Detector Method
# -----------------------------
AVOID_TIME_EDGES             = 0         # percentage of track-length not analysed on the edges.
FIRST_N_SECS                 = 0        # analyse first n seconds of each track (0 = full track)
SKIP_FIRST_MINUTE            = False
ANALYSIS_TYPE                = 'global'  # {'local', 'global'}
N_WINDOWS                    = 100       # if ANALYSIS_TYPE is 'local'
WINDOW_INCREMENT             = 100       # if ANALYSIS_TYPE is 'local'
KEY_PROFILE                  = 'bmtg3'   # {'edma', 'edmm', 'bmtg1', 'bmtg2', 'bmtg3'}
USE_THREE_PROFILES           = True
WITH_MODAL_DETAILS           = False


# ===================== #
# FUNCTION DECLARATIONS #
# ===================== #

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


def normalize_pcp_area(pcp):
    """
    Normalizes a pcp so that the sum of its content is 1,
    outputting a pcp with up to 3 decimal points.
    """
    pcp = np.divide(pcp, np.sum(pcp))
    new_format = []
    for item in pcp.tolist():
        new_format.append(round(item, 3))
    return new_format


def normalize_pcp_peak(pcp):
    """
    Normalizes a pcp so that the maximum value is 1,
    outputting a pcp with up to 3 decimal points.
    """
    pcp = np.multiply(pcp, (1 / np.max(pcp)))
    new_format = []
    for item in pcp:
        new_format.append(round(item, 3))
    print new_format
    return new_format


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


def transpose_pcp(pcp, tonic, pcp_size=36):
    """
    Takes an incoming pcp (assuming its first position
    corresponds to the note A and transposes it down so that
    the tonic note corresponds to the first place in the vector.
    """
    transposed = np.roll(pcp, (pcp_size / 12.0) * ((tonic - 9) % 12) * -1)
    return transposed


def extract_median_pcp(dir_estimations, dir_annotations, pcp_size=36):
    """
    Extracts the mean profile from a list of vectors.
    """
    list_estimations = os.listdir(dir_estimations)
    accumulate_profiles = []
    for item in list_estimations:
        if '.key' in item:
            root = open(dir_annotations + '/' + item, 'r')
            root = root.readline()
            root, mode = root[:root.find(' ')], root[root.find(' ') + 1:]
            pcp = open(dir_estimations + '/' + item, 'r')
            pcp = pcp.readline()
            pcp = pcp[pcp.rfind('\t') + 1:].split(', ')
            for i in range(pcp_size):
                pcp[i] = float(pcp[i])
            pcp = transpose_pcp(pcp, name_to_class(root))
            accumulate_profiles.append(pcp)
    return np.median(accumulate_profiles, axis=0)


def pcp_gate(pcp, threshold):
    """
    Zeroes vector elements with values under a certain threshold.
    """
    for i in range(len(pcp)):
        if pcp[i] < threshold:
            pcp[i] = 0
    return pcp


def pcp_sort(pcp):
    """
    Returns a new vector with sorted indexes of the incoming pcp vector.
    """
    pcp = pcp[:]
    idx = []
    for i in range(len(pcp)):
        new_index = pcp.index(np.max(pcp))
        idx.append(new_index)
        pcp[new_index] = -1
    return idx


def bin_to_pc(binary, pcp_size=36):
    """
    Returns the pitch-class of the specified pcp vector.
    It assumes (bin[0] == pc9) as implemeted in Essentia.
    """
    return int((binary / (pcp_size / 12.0)) + 9) % 12


def name_to_class(key):
    """
    Converts a note name to its pitch-class value.
    :type key: str
    """
    name2class = {'B#': 0, 'C': 0,
                  'C#': 1, 'Db': 1,
                  'D': 2,
                  'D#': 3, 'Eb': 3,
                  'E': 4, 'Fb': 4,
                  'E#': 5, 'F': 5,
                  'F#': 6, 'Gb': 6,
                  'G': 7,
                  'G#': 8, 'Ab': 8,
                  'A': 9, 'A#': 10,
                  'Bb': 10, 'B': 11,
                  'Cb': 11,
                  'none': 12, '-': 12}
    return name2class[key]


def mode_to_num(mode):
    """
    Converts a scale type into numeric values (maj = 0, min = 1).
    :type mode: str
    """
    mode2num = {'major': 0,
                'minor': 1,
                'ionian': 2,
                'harmonic': 3,
                'mixolydian': 4,
                'phrygian': 5,
                'fifth': 6,
                'monotonic': 7,
                'difficult': 8,
                'peak': 9,
                'flat': 10}
    return mode2num[mode]


def key_to_list(key):
    """
    Converts a key (i.e. C major) type into a
    numeric list in the form [tonic, mode].
    :type key: str
    """
    key = key.split(' ')
    key[-1] = key[-1].strip()
    if len(key) == 1:
        key = [name_to_class(key[0]), 0]
    else:
        key = [name_to_class(key[0]), mode_to_num(key[1])]
    return key


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


def estimate_key(input_audio_file, output_text_file):
    """
    This function estimates the overall key of an audio track
    optionaly with extra modal information.
    :type input_audio_file: str
    :type output_text_file: str
    """
    loader = estd.MonoLoader(filename=input_audio_file,
                             sampleRate=SAMPLE_RATE)
    hpf = estd.HighPass(cutoffFrequency=HIGHPASS_CUTOFF,
                        sampleRate=SAMPLE_RATE)
    window = estd.Windowing(size=WINDOW_SIZE,
                            type=WINDOW_SHAPE,
                            zeroPhase=False)
    rfft = estd.Spectrum(size=WINDOW_SIZE)
    sw = estd.SpectralWhitening(maxFrequency=MAX_HZ,
                                sampleRate=SAMPLE_RATE)
    speaks = estd.SpectralPeaks(magnitudeThreshold=SPECTRAL_PEAKS_THRESHOLD,
                                maxFrequency=MAX_HZ,
                                minFrequency=MIN_HZ,
                                maxPeaks=SPECTRAL_PEAKS_MAX,
                                sampleRate=SAMPLE_RATE)
    hpcp = estd.HPCP(bandPreset=HPCP_BAND_PRESET,
                     harmonics=HPCP_HARMONICS,
                     maxFrequency=MAX_HZ,
                     minFrequency=MIN_HZ,
                     nonLinear=HPCP_NON_LINEAR,
                     normalized=HPCP_NORMALIZE,
                     referenceFrequency=HPCP_REFERENCE_HZ,
                     sampleRate=SAMPLE_RATE,
                     size=HPCP_SIZE,
                     splitFrequency=HPCP_SPLIT_HZ,
                     weightType=HPCP_WEIGHT_TYPE,
                     windowSize=HPCP_WEIGHT_WINDOW_SEMITONES,
                     maxShifted=HPCP_SHIFT)
    if USE_THREE_PROFILES:
        key_1 = estd.KeyEDM3(pcpSize=HPCP_SIZE, profileType=KEY_PROFILE)
    else:
        key_1 = estd.KeyEDM(pcpSize=HPCP_SIZE, profileType=KEY_PROFILE)
    if WITH_MODAL_DETAILS:
        key_2 = estd.KeyExtended(pcpSize=HPCP_SIZE)
        keys_2 = []
    audio = hpf(hpf(hpf(loader())))
    duration = len(audio)
    frame_start = 0
    chroma = []
    keys_1 = []
    if SKIP_FIRST_MINUTE and duration > (SAMPLE_RATE * 60):
        audio = audio[SAMPLE_RATE * 60:]
        duration = len(audio)
    if FIRST_N_SECS > 0:
        if duration > (FIRST_N_SECS * SAMPLE_RATE):
            audio = audio[:FIRST_N_SECS * SAMPLE_RATE]
            duration = len(audio)
    if AVOID_TIME_EDGES > 0:
        initial_sample = (AVOID_TIME_EDGES * duration) / 100
        final_sample = duration - initial_sample
        audio = audio[initial_sample:final_sample]
        duration = len(audio)
    while frame_start <= (duration - WINDOW_SIZE):
        spek = rfft(window(audio[frame_start:frame_start + WINDOW_SIZE]))
        if sum(spek) <= 0.01:
            frame_start += HOP_SIZE
            continue
        p1, p2 = speaks(spek)
        if SPECTRAL_WHITENING:
            p2 = sw(spek, p1, p2)
        pcp = hpcp(p1, p2)
        pcp = pcp_gate(pcp, PCP_THRESHOLD)
        if not DETUNING_CORRECTION or DETUNING_CORRECTION_SCOPE == 'average':
            chroma.append(pcp)
        elif DETUNING_CORRECTION and DETUNING_CORRECTION_SCOPE == 'frame':
            pcp = shift_pcp(pcp, HPCP_SIZE)
            chroma.append(pcp)
        else:
            raise NameError("SHIFT_SCOPE must be set to 'frame' or 'average'.")
        if ANALYSIS_TYPE == 'local':
            if len(chroma) == N_WINDOWS:
                pcp = np.sum(chroma, axis=0)
                if DETUNING_CORRECTION and DETUNING_CORRECTION_SCOPE == 'average':
                    pcp = shift_pcp(list(pcp), HPCP_SIZE)
                pcp = pcp.tolist()
                local_key_1 = key_1(pcp)
                local_result_1 = local_key_1[0] + '\t' + local_key_1[1]
                keys_1.append(local_result_1)
                if WITH_MODAL_DETAILS:
                    local_key_2 = key_2(pcp)
                    local_result_2 = local_key_2[0] + '\t' + local_key_2[1]
                    keys_2.append(local_result_2)
                chroma = chroma[WINDOW_INCREMENT:]
        frame_start += WINDOW_SIZE
    if not chroma:
        return 'Silence'
    if ANALYSIS_TYPE == 'global':
        chroma = np.sum(chroma, axis=0)
        if DETUNING_CORRECTION and DETUNING_CORRECTION_SCOPE == 'average':
            chroma = shift_pcp(list(chroma), HPCP_SIZE)
        chroma = chroma.tolist()
        ordered_peaks = pcp_sort(chroma)
        peaks_pcs = []
        for item in ordered_peaks:
            peaks_pcs.append(bin_to_pc(item, HPCP_SIZE))
        estimation_1 = key_1(chroma)
        key_1 = estimation_1[0] + '\t' + estimation_1[1]
        if WITH_MODAL_DETAILS:
            estimation_2 = key_2(chroma)
            key_2 = estimation_2[0] + '\t' + estimation_2[1]
    elif ANALYSIS_TYPE == 'local':
        mode_1 = Counter(keys_1)
        key_1 = mode_1.most_common(1)[0][0]
        if WITH_MODAL_DETAILS:
            mode_2 = Counter(keys_2)
            key_2 = mode_2.most_common(1)[0][0]
    else:
        raise NameError("ANALYSIS_TYPE must be set to either 'local' or 'global'")
    filename = input_audio_file[input_audio_file.rfind('/') + 1:input_audio_file.rfind('.')]
    if WITH_MODAL_DETAILS:
        key_verbose = key_1 + '\t' + key_2
        key = key_verbose.split('\t')
        # SIMPLE RULES BASED ON THE MULTIPLE ESTIMATIONS TO IMPROVE THE RESULTS:
        # 1)
        if key[3] == 'monotonic' and key[0] == key[2]:
            key = '{0} minor'.format(key[0])
        # 2)
        # 3)
        # else we take the simple estimation as true:
        else:
            key = "{0}\t{1}".format(key[0], key[1])
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
    args = parser.parse_args()

    if not args.batch_mode:
        if not os.path.isfile(args.input):
            print "ERROR: Could not find '{0}'".format(args.input)
            sys.exit()
        elif os.path.isfile(args.input):
            print "\nAnalysing:\t{0}".format(args.input)
            print "Exporting to:\t{0}.".format(args.output)
            estimation = estimate_key(args.input, args.output)
            if args.verbose:
                print ":\t{0}".format(estimation),
        else:
            raise IOError("Unknown Error in single file mode")
    else:
        if os.path.isdir(args.input):
            analysis_folder = args.input[1 + args.input.rfind('/'):]
            if os.path.isfile(args.output):
                print "\nWARNING:"
                print "It seems that you are trying to write onto an existing file."
                print "In batch_mode, the output argument must be a directory.".format(args.output)
                print "Type 'edmkey.py -h' for help.\n"
                sys.exit()
            output_dir = results_directory(args.output)
            list_all_files = os.listdir(args.input)
            print "\nAnalysing audio files in:\t''{0}'.".format(args.input)
            print "Writing estimation files to:\t'{0}''.".format(args.output)
            count_files = 0
            for a_file in list_all_files:
                if any(soundfile_type in a_file for soundfile_type in VALID_FILE_TYPES):
                    input_file = args.input + '/' + a_file
                    output_file = args.output + '/' + a_file[:-4] + '.txt'
                    estimation = estimate_key(input_file, output_file)
                    if args.verbose:
                        print "{0} - {1}".format(input_file, estimation)
                    count_files += 1
            print "{0} audio files analysed.".format(count_files, clock())
        else:
            raise IOError("Unknown error in batch mode")
    print "Finished in:\t{0} s.".format(clock())
