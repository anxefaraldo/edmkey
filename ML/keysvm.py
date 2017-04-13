# from collections import Counter
import essentia.standard as estd

from conversions import *
from fodules.excel import *
from fodules.pcp import *
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
        # keys_2 = []
    audio = hpf(hpf(hpf(loader())))
    duration = len(audio)
    frame_start = 0
    chroma = []
    # keys_1 = []
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
        """
        if ANALYSIS_TYPE == 'local':
            if len(chroma) == N_WINDOWS:
                pcp = np.sum(chroma, axis=0)  # TODO: have a look at variance or std!
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
                """
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
        key_1 = estimation_1[0] + ' ' + estimation_1[1]
        keyn_1 = key_to_int(key_1)
        tonic_1 = name_to_class(estimation_1[0])
        scale_1 = mode_to_num(estimation_1[1])
        confidence_1 = estimation_1[2]
        if WITH_MODAL_DETAILS:
            estimation_2 = key_2(chroma)
            key_2 = estimation_2[0] + ' ' + estimation_2[1]
            tonic_2 = name_to_class(estimation_2[0])
            scale_2 = mode_to_num(estimation_2[1])
            confidence_2 = estimation_2[2]
        chroma = str(chroma)[1:-1]
        """
    elif ANALYSIS_TYPE == 'local':
        mode_1 = Counter(keys_1)
        key_1 = mode_1.most_common(1)[0][0]
        confidence_1 = 0.0
        peaks_pcs = ['N/A']
        chroma = ['N/A']
        if WITH_MODAL_DETAILS:
            mode_2 = Counter(keys_2)
            key_2 = mode_2.most_common(1)[0][0]
            confidence_2 = 0.0
            """
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
        # 2)
        # 3)
        # else we take the simple estimation as true:
        else:
            key = "{0} {1}".format(key[0], key[1])
            # keyn_2 = key_to_int(key)
        raw_output = "{0}, {1}, {2}, {3}, {4:.2f}, {5:.2f}, {6}, {7}, {8}, {9}, {10}, {11}".format(
                filename,  # todo arreglar el formato de esto
                key,
                chroma,
                str(peaks_pcs)[1:-1],
                keyn_1,
                tonic_1,
                scale_1,
                confidence_1,
                # keyn_2,
                tonic_2,
                scale_2,
                confidence_2,
                key_1,
                key_2)
    else:
        key = key_1
        raw_output = "{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7:.2f}, ".format(filename,
                                                                           key,
                                                                           chroma,
                                                                           str(peaks_pcs)[1:-1],
                                                                           keyn_1,
                                                                           tonic_1,
                                                                           scale_1,
                                                                           confidence_1)
    textfile = open(write_to + '/' + filename + '.key', 'w')
    textfile.write(raw_output)
    textfile.close()
    return key

"""
# This is the merged_results.csv file we are going to train with:
training_file = '/home/angel/Desktop/20160705201411-bmtg-wav/merged_results.csv'

# we use the whole bmtg collection for training!
features = features_from_csv(training_file, 2, 74)  # only 36 pcp values.
targets = stringcell_from_csv(training_file, 78)    # ground-truth of the file if keyExtended!
# filenames = stringcell_from_csv(training_file, 0)   # col. 0 stores the filename.
print len(features), 'files used for training.'


# Split data in train and test datasets
np.random.seed(0)  # A random permutation, to split the data randomly.
indices = np.random.permutation(len(features))
features_train = features[indices[:-10]]
targets_train = targets[indices[:-10]]
filenames_train = filenames[indices[:-10]]
features_test = features[indices[-10:]]
targets_test = targets[indices[-10:]]
filenames_test = filenames[indices[-10:]]

# here is the actual support vector machine.
svc = svm.LinearSVC()
svc.fit(features, targets)

# NOW WE NEED TO LOAD DIFFERENT DATASETS TO TEST!
analysis_file = '/home/angel/Desktop/20160705200749-gs-wav/merged_results.csv'
features = features_from_csv(analysis_file, 2, 74)
filenames = stringcell_from_csv(analysis_file, 0)

an_folder = analysis_file[:analysis_file.rfind('/')]
for i in range(len(features)):
    prediction = svc.predict(features[i].reshape(-1, 72))
    prediction = "{0}, ".format(str(prediction)[2:-2])
    append_results = open(an_folder + '/' + filenames[i] + '.key', 'a')
    append_results.write(prediction)
    append_results.close()

"""
