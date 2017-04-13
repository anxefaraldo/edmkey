#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

from fileutils import make_unique_dir
from collections import Counter
import essentia.standard as estd

from conversions import *
from pcp import *
from settings import *


def estimate_key(soundfile, write_to):
    """
    This function estimates the overall key of an audio track
    optionaly with extra modal information.
    :type soundfile: str
    :type write_to: str
    """
    loader = estd.MonoLoader(filename=soundfile,
                             sampleRate=SAMPLE_RATE)
    cut = estd.FrameCutter(frameSize=WINDOW_SIZE,
                           hopSize=HOP_SIZE)
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
        keys_2 = []
    audio = hpf(hpf(hpf(loader())))
    duration = len(audio)
    frame_start = 0
    chroma = []
    keys_1 = []
    if SKIP_FIRST_N_SECS and duration > (SAMPLE_RATE * 60):
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
    # number_of_frames = duration / HOP_SIZE #### NEWLINE
    while frame_start <= (duration - WINDOW_SIZE):
        spek = rfft(window(audio[frame_start:frame_start + WINDOW_SIZE]))
    #for frame in range(number_of_frames):
    #    spek = rfft(window(cut(audio)))
        # if sum(spek) <= 0.01:
        #     frame_start += HOP_SIZE
        #     continue
        p1, p2 = speaks(spek)
        if SPECTRAL_WHITENING:
            p2 = sw(spek, p1, p2)
        pcp = hpcp(p1, p2)
        if np.sum(pcp) > 0:
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
                local_result_1 = local_key_1[0] + ' ' + local_key_1[1]
                keys_1.append(local_result_1)
                if WITH_MODAL_DETAILS:
                    local_key_2 = key_2(pcp)
                    local_result_2 = local_key_2[0] + ' ' + local_key_2[1]
                    keys_2.append(local_result_2)
                chroma = chroma[WINDOW_INCREMENT:]
        frame_start += HOP_SIZE # I think here was the problem!
    if not chroma:
        return 'Silence'
    if ANALYSIS_TYPE == 'global':
        chroma = np.sum(chroma, axis=0)
        chroma = normalize_pcp_peak(chroma)
        chroma = pcp_gate(chroma, PCP_THRESHOLD)
        if DETUNING_CORRECTION and DETUNING_CORRECTION_SCOPE == 'average':
            chroma = shift_pcp(list(chroma), HPCP_SIZE)
        chroma = chroma.tolist()
        ordered_peaks = pcp_sort(chroma)
        peaks_pcs = []
        for peak in ordered_peaks:
            peaks_pcs.append(bin_to_pc(peak, HPCP_SIZE))
        estimation_1 = key_1(chroma)
        key_1 = estimation_1[0] + ' ' + estimation_1[1]
        # keyn_1 = key_to_int(key_1)
        # tonic_1 = name_to_class(estimation_1[0])
        # scale_1 = mode_to_num(estimation_1[1])
        # confidence_1 = estimation_1[2]
        if WITH_MODAL_DETAILS:
            estimation_2 = key_2(chroma)
            key_2 = estimation_2[0] + ' ' + estimation_2[1]
            # tonic_2 = name_to_class(estimation_2[0])
            # scale_2 = mode_to_num(estimation_2[1])
            # confidence_2 = estimation_2[2]
        # chroma = str(chroma)[1:-1]
    elif ANALYSIS_TYPE == 'local':
        mode_1 = Counter(keys_1)
        key_1 = mode_1.most_common(1)[0][0]
        # keyn_1 = key_to_int(key_1)
        # confidence_1 = 0.0
        # peaks_pcs = ['N/A']
        # chroma = ['N/A']
        if WITH_MODAL_DETAILS:
            mode_2 = Counter(keys_2)
            key_2 = mode_2.most_common(1)[0][0]
            # confidence_2 = 0.0
    else:
        raise NameError("ANALYSIS_TYPE must be set to either 'local' or 'global'")
    filename = soundfile[soundfile.rfind('/') + 1:soundfile.rfind('.')]
    if WITH_MODAL_DETAILS:
        key_verbose = key_1 + ' ' + key_2
        key = key_verbose.split(' ')
        # SIMPLE RULES BASED ON THE MULTIPLE ESTIMATIONS TO IMPROVE THE RESULTS:
        # 1)
        if key[3] == 'monotonic' and key[0] == key[2]:
            key = '{0} minor'.format(key[0])
        else:
            key = "{0} {1}".format(key[0], key[1])
            # keyn_2 = key_to_int(key)
        # raw_output = "{0}, {1}, {2}, {3}, {4:.2f}, {5:.2f}, {6}, {7}, {8}, {9}, {10}, {11}".format(
         #       filename, key, chroma, str(peaks_pcs)[1:-1], keyn_1, tonic_1, scale_1, confidence_1, # keyn_2,
         #       tonic_2, scale_2, confidence_2, key_1, key_2)
    else:
        key = key_1
        # raw_output = "{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7:.2f}, ".format(
         #       filename, key, chroma, str(peaks_pcs)[1:-1], keyn_1, tonic_1, scale_1, confidence_1)
    textfile = open(write_to + '/' + filename + '.key', 'w')
    if RAW_OUTPUT:
        # textfile.write(raw_output)
        pass
    else:
        textfile.write(key + '\n')
    textfile.close()
    return key


if __name__ == "__main__":

    from time import clock
    from argparse import ArgumentParser

    clock()
    conf_file = open('./settings.py', 'r')

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
