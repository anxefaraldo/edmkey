import essentia.standard as estd

from conversions import *
from fodules.excel import *
from fodules.pcp import *
from settings import *


def get_features(soundfile, target):
    """
    This function estimates the overall key of an audio track
    optionaly with extra modal information.
    :type soundfile: str
    :type target: str
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
    key_1 = estd.KeyEDM3(pcpSize=HPCP_SIZE, profileType=KEY_PROFILE)
    key_2 = estd.KeyExtended(pcpSize=HPCP_SIZE)
    audio = hpf(hpf(hpf(loader())))
    duration = len(audio)
    frame_start = 0
    chroma = []
    feature_vector = []
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
        frame_start += WINDOW_SIZE
    if not chroma:
        return 'Silence'
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
    feature_vector.append(key_to_int(key_1))               # key1 as int
    feature_vector.append(name_to_class(estimation_1[0]))  # tonic1 as int
    feature_vector.append(mode_to_num(estimation_1[1]))    # scale1 as int
    feature_vector.append(estimation_1[2])                 # confidence1
    estimation_2 = key_2(chroma)
    # key_2 = estimation_2[0] + ' ' + estimation_2[1]
    feature_vector.append(name_to_class(estimation_2[0]))  # tonic2 as int
    feature_vector.append(mode_to_num(estimation_2[1]))    # mode2 as int
    feature_vector.append(estimation_2[2])                 # confidence2
    # feature_vector.append(chroma)
    filename = soundfile[soundfile.rfind('/') + 1:soundfile.rfind('.')]
    #textfile = open(write_to + '/' + filename + '.key', 'w')
    #textfile.write(str(feature_vector))
    #textfile.close()
    feature_vector = np.array(feature_vector)
    feature_vector = np.concatenate((feature_vector, chroma), axis=0)
    return feature_vector, target



"""
# This is the merged_results.csv file we are going to train with:
training_file = '/home/angel/Desktop/20160705201411-bmtg-wav/merged_results.csv'

# we use the whole bmtg collection for training!
features = features_from_csv(training_file, 2, 74)  # only 36 pcp values.
targets = stringcell_from_csv(training_file, 78)    # ground-truth of the file if keyExtended!
# filenames = stringcell_from_csv(training_file, 0)   # col. 0 stores the filename.
print len(features), 'files used for training.'

filenames
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
