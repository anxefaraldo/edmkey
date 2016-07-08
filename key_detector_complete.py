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
import sys, os, re
import numpy as np
# import essentia as e
import essentia.standard as estd
from random import sample
from time import time as tiempo
from time import clock as reloj


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
    key = key.split(' ')
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
        results = list(np.divide(results, size))
        results.append(np.mean(list_with_weighted_results))
        return results


def shift_vector(pcp, pcp_size=12):
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

if analysis_mode == 'title':
    """TODO: for both collection and genre, I have to come up with a method that analyses
     es everything if nothing is specified.
     ['KF100', 'KF1000', 'GSANG', 'ENDO100', 'DJTECHTOOLS60']"""
    collection     = ['KF100', 'KF1000', 'GSANG', 'ENDO100', 'DJTECHTOOLS60']
    genre          = ['edm']  # ['edm', 'non-edm']
    modality       = ['minor', 'major']  # ['major', 'minor']
    limit_analysis = 0  # Limit key to N random tracks. 0 = all samples matching above criteria.

"""
Settings for Classical Music:
==========================
SPECTRAL_WHITENING   = False
window_size          = 2048
jump_frames          = 4
min_frequency        = 25
max_frequency        = 1000
profile_type         = 'temperley2005'

'temperley2005 works better with spectral whitening on.
Others, like 'noland' and 'temperley' perform better with max_frequency = 1700
and without spectral whitening

Setiings for EDM:
=================
SPECTRAL_WHITENING   = True
DETUNING_CORRECTION       = True
window_size          = 4096
jump_frames          = 4
min_frequency        = 25
max_frequency        = 3500
profile_type         = 'edmm'

"""
# ANALYSIS PARAMETERS
# ===================
# faraldo:
avoid_edges          = 0  # % of duration at the beginning and end that is not analysed.
first_n_secs         = 0  # only analyse the first N seconds of each track (o = full track)
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
jump_frames          = 4  # 1 = analyse every frame; 2 = analyse every other frame; etc.
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
profile_type         = 'edmm'
use_three_chords     = False  # BEWARE: False executes the extra code including all triads!
use_polyphony        = False
num_harmonics        = 15   # when use_polyphony == True
slope                = 0.2  # when use_polyphony == True

# ////////////////////////////////////////////////////////////////////////////


def key_detector():
    reloj()
    # create directory to write the results with an unique time id:
    if results_to_file or results_to_csv:
        uniqueTime = str(int(tiempo()))
        wd = os.getcwd()
        temp_folder = wd + '/KeyDetection_' + uniqueTime
        os.mkdir(temp_folder)
    if results_to_csv:
        import csv
        csvFile = open(temp_folder + '/Estimation_&_PCP.csv', 'w')
        lineWriter = csv.writer(csvFile, delimiter=',')
    # retrieve files and filenames according to the desired settings:
    if analysis_mode == 'title':
        allfiles = os.listdir(audio_folder)
        if '.DS_Store' in allfiles: allfiles.remove('.DS_Store')
        for item in collection: collection[collection.index(item)] = ' > ' + item + '.'
        for item in genre: genre[genre.index(item)] = ' < ' + item + ' > '
        for item in modality:modality[modality.index(item)] = ' ' + item + ' < '
        analysis_files = []
        for item in allfiles:
            if any(e1 for e1 in collection if e1 in item):
                if any(e2 for e2 in genre if e2 in item):
                    if any(e3 for e3 in modality if e3 in item):
                        analysis_files.append(item)
        song_instances = len(analysis_files)
        print song_instances, 'songs matching the selected criteria:'
        print collection, genre, modality
        if limit_analysis == 0:
            pass
        elif limit_analysis < song_instances:
            analysis_files = sample(analysis_files, limit_analysis)
            print "taking", limit_analysis, "random samples...\n"
    else:
        analysis_files = os.listdir(audio_folder)
        if '.DS_Store' in analysis_files:
            analysis_files.remove('.DS_Store')
        print len(analysis_files), '\nsongs in folder.\n'
        groundtruth_files = os.listdir(groundtruth_folder)
        if '.DS_Store' in groundtruth_files:
            groundtruth_files.remove('.DS_Store')
    # ANALYSIS
    # ========
    if verbose:
        print "ANALYSING INDIVIDUAL SONGS..."
        print "============================="
    if confusion_matrix:
        matrix = 24 * 24 * [0]
    mirex_scores = []
    for item in analysis_files:
        # INSTANTIATE ESSENTIA ALGORITHMS
        # ===============================
        loader = estd.MonoLoader(filename=audio_folder + '/' + item,
                                 sampleRate=sample_rate)
        cut    = estd.FrameCutter(frameSize=window_size,
                                  hopSize=hop_size)
        window = estd.Windowing(size=window_size,
                                type=window_type)
        rfft   = estd.Spectrum(size=window_size)
        sw     = estd.SpectralWhitening(maxFrequency=max_frequency,
                                        sampleRate=sample_rate)
        speaks = estd.SpectralPeaks(magnitudeThreshold=magnitude_threshold,
                                    maxFrequency=max_frequency,
                                    minFrequency=min_frequency,
                                    maxPeaks=max_peaks,
                                    sampleRate=sample_rate)
        hpcp   = estd.HPCP(bandPreset=band_preset,
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
        key    = estd.Key(numHarmonics=num_harmonics,
                          pcpSize=hpcp_size,
                          profileType=profile_type,
                          slope=slope,
                          usePolyphony=use_polyphony,
                          useThreeChords=use_three_chords)
        # ACTUAL ANALYSIS
        # ===============
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
                    vector = shift_vector(vector, hpcp_size)
                    chroma.append(vector)
                else:
                    print "SHIFT_SCOPE must be set to 'frame' or 'average'"
        chroma = np.mean(chroma, axis=0)
        if shift_spectrum and shift_scope == 'average':
            chroma = shift_vector(chroma, hpcp_size)
        estimation = key(chroma.tolist())
        result = estimation[0] + '\t' + estimation[1]
        confidence = estimation[2]
        if results_to_csv:
            chroma = list(chroma)
        # MIREX EVALUATION:
        # ================
        if analysis_mode == 'title':
            ground_truth = item[item.find(' = ')+3:item.rfind(' < ')]
            if verbose and confidence < confidence_threshold:
                print item[:item.rfind(' = ')]
                print 'G:', ground_truth, '|| P:',
            if results_to_csv:
                title = item[:item.rfind(' = ')]
                lineWriter.writerow([title, ground_truth, chroma[0], chroma[1], chroma[2], chroma[3], chroma[4], chroma[5], chroma[6], chroma[7], chroma[8], chroma[9], chroma[10], chroma[11], chroma[12], chroma[13], chroma[14], chroma[15], chroma[16], chroma[17], chroma[18], chroma[19], chroma[20], chroma[21], chroma[22], chroma[23], chroma[24], chroma[25], chroma[26], chroma[27], chroma[28], chroma[29], chroma[30], chroma[31], chroma[32], chroma[33], chroma[34], chroma[35], result])
            ground_truth = key_to_list(ground_truth)
            estimation = key_to_list(result)
            score = mirex_score(ground_truth, estimation)
            mirex_scores.append(score)
        else:
            filename_to_match = item[:item.rfind('.')] + '.txt'
            print filename_to_match
            if filename_to_match in groundtruth_files:
                groundtruth_file = open(groundtruth_folder+'/'+filename_to_match, 'r')
                ground_truth = groundtruth_file.readline()
                if "\t" in ground_truth:
                    ground_truth = re.sub("\t", " ", ground_truth)
                if results_to_csv:
                    lineWriter.writerow([filename_to_match, chroma[0], chroma[1], chroma[2], chroma[3], chroma[4], chroma[5], chroma[6], chroma[7], chroma[8], chroma[9], chroma[10], chroma[11], chroma[12], chroma[13], chroma[14], chroma[15], chroma[16], chroma[17], chroma[18], chroma[19], chroma[20], chroma[21], chroma[22], chroma[23], chroma[24], chroma[25], chroma[26], chroma[27], chroma[28], chroma[29], chroma[30], chroma[31], chroma[32], chroma[33], chroma[34], chroma[35], result])
                ground_truth = key_to_list(ground_truth)
                estimation = key_to_list(result)
                score = mirex_score(ground_truth, estimation)
                mirex_scores.append(score)
            else:
                print "FILE NOT FOUND... Skipping it from evaluation.\n"
                continue
        # CONFUSION MATRIX:
        # ================
        if confusion_matrix:
            xpos = (ground_truth[0] + (ground_truth[0] * 24)) + (-1*(ground_truth[1]-1) * 24 * 12)
            ypos = ((estimation[0] - ground_truth[0]) + (-1 * (estimation[1]-1) * 12))
            matrix[(xpos+ypos)] =+ matrix[(xpos+ypos)] + 1
        if verbose and confidence < confidence_threshold:
            print result, '(%.2f)' % confidence, '|| SCORE:', score, '\n'
        # WRITE RESULTS TO FILE:
        # =====================
        if results_to_file:
            with open(temp_folder + '/' + item[:-3]+'txt', 'w') as textfile:
                textfile.write(result)
                textfile.close()
    if results_to_csv:
        csvFile.close()
    print len(mirex_scores), "files analysed in", reloj(), "secs.\n"
    if confusion_matrix:
        matrix = np.matrix(matrix)
        matrix = matrix.reshape(24,24)
        print matrix
        if results_to_file:
            np.savetxt(temp_folder + '/_confusion_matrix.csv', matrix, fmt='%i', delimiter=',', header='C,C#,D,Eb,E,F,F#,G,G#,A,Bb,B,Cm,C#m,Dm,Ebm,Em,Fm,F#m,Gm,G#m,Am,Bbm,Bm')
    # MIREX RESULTS
    # =============
    evaluation_results = mirex_evaluation(mirex_scores)
    print evaluation_results
    # WRITE INFO TO FILE
    # ==================
    if results_to_file:
        settings = "SETTINGS\n========\nAvoid edges ('%' of duration disregarded at both ends (0 = complete)) = "+str(avoid_edges)+"\nfirst N secs = "+str(first_n_secs)+"\nshift spectrum to fit tempered scale = "+str(shift_spectrum)+"\nspectral whitening = "+str(spectral_whitening)+"\nsample rate = "+str(sample_rate)+"\nwindow size = "+str(window_size)+"\nhop size = "+str(hop_size)+"\nmagnitude threshold = "+str(magnitude_threshold)+"\nminimum frequency = "+str(min_frequency)+"\nmaximum frequency = "+str(max_frequency)+"\nmaximum peaks = "+str(max_peaks)+"\nband preset = "+str(band_preset)+"\nsplit frequency = "+str(split_frequency)+"\nharmonics = "+str(harmonics)+"\nnon linear = "+str(non_linear)+"\nnormalize = "+str(normalize)+"\nreference frequency = "+str(reference_frequency)+"\nhpcp size = "+str(hpcp_size)+"\nweigth type = "+weight_type+"\nweight window size in semitones = "+str(weight_window_size)+"\nharmonics key = "+str(num_harmonics)+"\nslope = "+str(slope)+"\nprofile = "+profile_type+"\npolyphony = "+str(use_polyphony)+"\nuse three chords = "+str(use_three_chords)
        results_for_file = "\n\nEVALUATION RESULTS\n==================\nCorrect: "+str(evaluation_results[0])+"\nFifth:  "+str(evaluation_results[1])+"\nRelative: "+str(evaluation_results[2])+"\nParallel: "+str(evaluation_results[3])+"\nError: "+str(evaluation_results[4])+"\nWeighted: "+str(evaluation_results[5])
        write_to_file = open(temp_folder + '/_SUMMARY.txt', 'w')
        write_to_file.write(settings)
        write_to_file.write(results_for_file)
        if analysis_mode == 'title':
            corpus = "\n\nANALYSIS CORPUS\n===============\n" + str(collection) + '\n' + str(genre) + '\n' + str(modality) + '\n\n' + str(len(mirex_scores)) + " files analysed.\n"
            write_to_file.write(corpus)
        write_to_file.close()


if __name__ == "__main__":
    if analysis_mode == 'txt':
        try:
            audio_folder = sys.argv[1]
            groundtruth_folder = sys.argv[2]
        except:
            print "ERROR! In 'txt' mode you should provide two arguments:"
            print "filename.py <route to audio> <route to ground-truth annotations>\n"
            sys.exit()
    elif analysis_mode == 'title':
        try:
            audio_folder = sys.argv[1]
        except:
            audio_folder = "/Users/angel/GoogleDrive/EDM/EDM_Collections/KEDM_mono_wav"
            print "-------------------------------"
            print "Analysis folder NOT provided. Analysing contents in:"
            print audio_folder
            print "If you want to analyse a different folder you should type:"
            print "filename.py route-to-folder-with-audio-and-annotations-in-filename"
            print "-------------------------------"
    else:
        print "Unrecognised key mode. It should be either 'txt' or 'title'."
        sys.exit()
    key_detector()
