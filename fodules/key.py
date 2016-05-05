from conf import *
import numpy as np
from collections import Counter
import essentia.standard as estd
from fodules.pcp import shift_pcp


def key_estimate(soundfile, write_to):
    """
    Estimates the overall key of an audio track.
    :type soundfile: str
    :type write_to: str
    """
    loader = estd.MonoLoader(filename=soundfile,
                             sampleRate=SAMPLE_RATE)
    hpf = estd.HighPass(cutoffFrequency=HIGHPASS_CUTOFF,
                        sampleRate=SAMPLE_RATE)
    window = estd.Windowing(size=WINDOW_SIZE,
                            type=WINDOW_TYPE,
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
                     windowSize=HPCP_WEIGHT_WINDOW_SIZE,
                     maxShifted=HPCP_SHIFT)
    if USE_THREE_PROFILES:
        key = estd.Key2(pcpSize=HPCP_SIZE, profileType=KEY_PROFILE)
    else:
        key = estd.KeyEDM(pcpSize=HPCP_SIZE, profileType=KEY_PROFILE)
    audio = hpf(hpf(hpf(loader())))
    duration = len(audio)
    frame_start = 0
    chroma = []
    keys = []
    if SKIP_FIRST_MINUTE and duration > (SAMPLE_RATE * 60):
        audio = audio[SAMPLE_RATE * 60:]
        duration = len(audio)
    if FIRST_N_SECS > 0:
        if duration > (FIRST_N_SECS * SAMPLE_RATE):
            audio = audio[:FIRST_N_SECS * SAMPLE_RATE]
            duration = len(audio)
    if AVOID_EDGES > 0:
        initial_sample = (AVOID_EDGES * duration) * 0.01
        final_sample = duration - initial_sample
        audio = audio[initial_sample:final_sample]
        duration = len(audio)
    while frame_start <= (duration - WINDOW_SIZE):
        spek = rfft(window(audio[frame_start:frame_start + WINDOW_SIZE]))
        if sum(spek) <= 0.01:
            frame_start += HOP_SIZE
            continue
        p1, p2 = speaks(spek)  # p1 = freqs; p2 = magnitudes
        if SPECTRAL_WHITENING:
            p2 = sw(spek, p1, p2)
        pcp = hpcp(p1, p2)
        if not DETUNING_CORRECTION or SHIFT_SCOPE == 'average':
            chroma.append(pcp)
        elif DETUNING_CORRECTION and SHIFT_SCOPE == 'frame':
            pcp = shift_pcp(pcp, HPCP_SIZE)
            chroma.append(pcp)
        else:
            raise NameError("SHIFT_SCOPE must be set to 'frame' or 'average'")
        if ANALYSIS_TYPE == 'local':
            if len(chroma) == N_WINDOWS:
                pcp = np.sum(chroma, axis=0)
                if DETUNING_CORRECTION and SHIFT_SCOPE == 'average':
                    pcp = shift_pcp(list(pcp), HPCP_SIZE)
                pcp = pcp.tolist()
                local_key = key(pcp)
                local_result = local_key[0] + ' ' + local_key[1]
                keys.append(local_result)
                chroma = chroma[WINDOW_INCREMENT:]
        frame_start += HOP_SIZE
    if not chroma:
        return 'Silence',
    if ANALYSIS_TYPE == 'global':
        chroma = np.sum(chroma, axis=0)  # TODO: have a look at variance or std!
        if DETUNING_CORRECTION and SHIFT_SCOPE == 'average':
            chroma = shift_pcp(list(chroma), HPCP_SIZE)
        chroma = chroma.tolist()
        estimation = key(chroma)
        chroma = str(chroma)[1:-1]
        key = estimation[0] + ' ' + estimation[1]
        confidence = estimation[2]
    elif ANALYSIS_TYPE == 'local':
        mode = Counter(keys)
        key = mode.most_common(1)[0][0]
        confidence = 0.0
        chroma = ['N/A']
    else:
        raise NameError("ANALYSIS_TYPE must be set to either 'local' or 'global'")
    if 'minor2' in key:
        key.split(' ')
        key = "{0} minor".format(key[0])
    filename = soundfile[soundfile.rfind('/') + 1:soundfile.rfind('.')]
    raw_output = "{0}\t{1}\t{2:.2f}\t{3}".format(filename,
                                                 key,
                                                 confidence,
                                                 chroma)
    textfile = open(write_to + '/' + filename + '.key', 'w')
    textfile.write(raw_output)
    textfile.close()
    return key


def key_estimate_extended(soundfile, write_to):
    """This function estimates the overall key of an audio track.
    :type soundfile: str
    :type write_to: str"""
    loader = estd.MonoLoader(filename=soundfile,
                             sampleRate=SAMPLE_RATE)
    hpf = estd.HighPass(cutoffFrequency=HIGHPASS_CUTOFF,
                        sampleRate=SAMPLE_RATE)
    window = estd.Windowing(size=WINDOW_SIZE,
                            type=WINDOW_TYPE,
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
                     windowSize=HPCP_WEIGHT_WINDOW_SIZE,
                     maxShifted=HPCP_SHIFT)
    if USE_THREE_PROFILES:
        key_1 = estd.Key2(pcpSize=HPCP_SIZE, profileType=KEY_PROFILE)
    else:
        key_1 = estd.KeyEDM(pcpSize=HPCP_SIZE, profileType=KEY_PROFILE)
    key_2 = estd.KeyExtended(pcpSize=HPCP_SIZE)
    audio = hpf(hpf(hpf(loader())))
    duration = len(audio)
    frame_start = 0
    chroma = []
    keys_1 = []
    keys_2 = []
    if SKIP_FIRST_MINUTE and duration > (SAMPLE_RATE * 60):
        audio = audio[SAMPLE_RATE * 60:]
        duration = len(audio)
    if FIRST_N_SECS > 0:
        if duration > (FIRST_N_SECS * SAMPLE_RATE):
            audio = audio[:FIRST_N_SECS * SAMPLE_RATE]
            duration = len(audio)
    if AVOID_EDGES > 0:
        initial_sample = (AVOID_EDGES * duration) / 100
        final_sample = duration - initial_sample
        audio = audio[initial_sample:final_sample]
        duration = len(audio)
    while frame_start < (duration - WINDOW_SIZE):
        spek = rfft(window(audio[frame_start:frame_start + WINDOW_SIZE]))
        if sum(spek) <= 0.01:
            frame_start += HOP_SIZE
            continue
        p1, p2 = speaks(spek)
        if SPECTRAL_WHITENING:
            p2 = sw(spek, p1, p2)
        pcp = hpcp(p1, p2)
        if not DETUNING_CORRECTION or SHIFT_SCOPE == 'average':
            chroma.append(pcp)
        elif DETUNING_CORRECTION and SHIFT_SCOPE == 'frame':
            pcp = shift_pcp(pcp, HPCP_SIZE)
            chroma.append(pcp)
        else:
            raise NameError("SHIFT_SCOPE must be set to 'frame' or 'average'.")
        if ANALYSIS_TYPE == 'local':
            if len(chroma) == N_WINDOWS:
                pcp = np.sum(chroma, axis=0)
                if DETUNING_CORRECTION and SHIFT_SCOPE == 'average':
                    pcp = shift_pcp(list(pcp), HPCP_SIZE)
                pcp = pcp.tolist()
                local_key_1 = key_1(pcp)
                local_result_1 = local_key_1[0] + ' ' + local_key_1[1]
                local_key_2 = key_2(pcp)
                local_result_2 = local_key_2[0] + ' ' + local_key_2[1]
                keys_1.append(local_result_1)
                keys_2.append(local_result_2)
                chroma = chroma[WINDOW_INCREMENT:]
        frame_start += WINDOW_SIZE
    if not chroma:
        return 'Silence'
    if ANALYSIS_TYPE == 'global':
        chroma = np.sum(chroma, axis=0)
        if DETUNING_CORRECTION and SHIFT_SCOPE == 'average':
            chroma = shift_pcp(list(chroma), HPCP_SIZE)
        chroma = chroma.tolist()
        peak_pcp = int(((chroma.index(np.max(chroma)) / (HPCP_SIZE / 12.0)) + 9) % 12)
        estimation_1 = key_1(chroma)
        key_1 = estimation_1[0] + ' ' + estimation_1[1]
        confidence_1 = estimation_1[2]
        estimation_2 = key_2(chroma)
        key_2 = estimation_2[0] + ' ' + estimation_2[1]
        confidence_2 = estimation_2[2]
        chroma = str(chroma)[1:-1]
    elif ANALYSIS_TYPE == 'local':
        mode_1 = Counter(keys_1)
        key_1 = mode_1.most_common(1)[0][0]
        mode_2 = Counter(keys_2)
        key_2 = mode_2.most_common(1)[0][0]
        confidence_1 = 0.0
        confidence_2 = 0.0
        peak_pcp = -1
        chroma = ['N/A']
    else:
        raise NameError("ANALYSIS_TYPE must be set to either 'local' or 'global'")
    key_verbose = key_1 + ' ' + key_2
    key = key_verbose.split(' ')
    #  NOW WE APPLY SOME SIMPLE RULES BASED ON THE MULTIPLE ESTIMATIONS TO IMPROVE THE RESULTS:
    # 1)
    if key[3] == 'monotonic' and key[0] == key[2]:
        key = '{0} minor'.format(key[0])
    # 2)
    # 3)
    # or else take the simple estimation as true:
    elif key[1] == 'minor2':
        key = "{0} minor".format(key[0])
    else:
        key = "{0} {1}".format(key[0], key[1])
    filename = soundfile[soundfile.rfind('/') + 1:soundfile.rfind('.')]
    raw_output = "{0}\t{1}\t{2:.2f}/{3:.2f}\t{4}\t{5}\t{6}".format(filename,
                                                                   key,
                                                                   confidence_1,
                                                                   confidence_2,
                                                                   chroma,
                                                                   peak_pcp,
                                                                   key_verbose)
    textfile = open(write_to + '/' + filename + '.key', 'w')
    textfile.write(raw_output)
    textfile.close()
    return key


def key_estimate_multiscope(soundfile, write_to):
    """
    Estimates the overall key of an audio track.
    :type soundfile: str
    :type write_to: str
    """
    loader = estd.MonoLoader(filename=soundfile,
                             sampleRate=SAMPLE_RATE)
    hpf = estd.HighPass(cutoffFrequency=HIGHPASS_CUTOFF,
                        sampleRate=SAMPLE_RATE)
    window = estd.Windowing(size=WINDOW_SIZE,
                            type=WINDOW_TYPE,
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
                     windowSize=HPCP_WEIGHT_WINDOW_SIZE,
                     maxShifted=HPCP_SHIFT)
    if USE_THREE_PROFILES:
        key = estd.Key2(pcpSize=HPCP_SIZE, profileType=KEY_PROFILE)
    else:
        key = estd.KeyEDM(pcpSize=HPCP_SIZE, profileType=KEY_PROFILE)
    audio = hpf(hpf(hpf(loader())))
    duration = len(audio)
    frame_start = 0
    chroma_local = []
    chroma_global = []
    local_keys = []
    if SKIP_FIRST_MINUTE and duration > (SAMPLE_RATE * 60):
        audio = audio[SAMPLE_RATE * 60:]
        duration = len(audio)
    if FIRST_N_SECS > 0:
        if duration > (FIRST_N_SECS * SAMPLE_RATE):
            audio = audio[:FIRST_N_SECS * SAMPLE_RATE]
            duration = len(audio)
    if AVOID_EDGES > 0:
        initial_sample = (AVOID_EDGES * duration) * 0.01
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
        if not DETUNING_CORRECTION or SHIFT_SCOPE == 'average':
            chroma_global.append(pcp)
            chroma_local.append(pcp)
        elif DETUNING_CORRECTION and SHIFT_SCOPE == 'frame':
            pcp = shift_pcp(pcp, HPCP_SIZE)
            chroma_global.append(pcp)
            chroma_local.append(pcp)
        else:
            raise NameError("SHIFT_SCOPE must be set to 'frame' or 'average'")
        if len(chroma_local) == N_WINDOWS:
            pcp = np.sum(chroma_local, axis=0)
            if DETUNING_CORRECTION and SHIFT_SCOPE == 'average':
                pcp = shift_pcp(list(pcp), HPCP_SIZE)
            pcp = pcp.tolist()
            estimation_local = key(pcp)
            key_local = estimation_local[0] + ' ' + estimation_local[1]
            local_keys.append(key_local)
            chroma_local = chroma_local[WINDOW_INCREMENT:]
        frame_start += HOP_SIZE
    if not chroma_global:
        return 'Silence'
    chroma_global = np.sum(chroma_global, axis=0)
    if DETUNING_CORRECTION and SHIFT_SCOPE == 'average':
        chroma_global = shift_pcp(list(chroma_global), HPCP_SIZE)
    chroma_global = chroma_global.tolist()
    peak_global = int(((chroma_global.index(np.max(chroma_global)) / (HPCP_SIZE / 12.0)) + 9) % 12)
    estimation_global = key(chroma_global)
    chroma_global = str(chroma_global)[1:-1]
    key_global = estimation_global[0] + ' ' + estimation_global[1]
    confidence_global = estimation_global[2]
    local_keys = Counter(local_keys)
    list_of_keys = local_keys.most_common(12)
    key_local = local_keys.most_common(1)[0][0]
    if key_global == key_local:
        key = key_global
    else:
        key = [key_global, key_local]
        # key = key[randint(0, 1)]
        key = key[0]  # TODO: for the moment use global estimations for evaluation!
    filename = soundfile[soundfile.rfind('/') + 1:soundfile.rfind('.')]
    raw_output = "{0}\t{1}\t{2:.2f}\t{3}\t{4}\t{5}\t{6}\t{7}".format(filename,
                                                                     key,
                                                                     confidence_global,
                                                                     chroma_global,
                                                                     peak_global,
                                                                     key_global,
                                                                     key_local,
                                                                     list_of_keys)
    textfile = open(write_to + '/' + filename + '.key', 'w')
    textfile.write(raw_output)
    textfile.close()
    return key


def key_estimate_baseline(soundfile, write_to):
    """
    Estimates the overall key of an audio track.
    :type soundfile: str
    :type write_to: str
    """
    loader = estd.MonoLoader(filename=soundfile,
                             sampleRate=SAMPLE_RATE)
    window = estd.Windowing(size=WINDOW_SIZE,
                            type=WINDOW_TYPE,
                            zeroPhase=False)  # True = cos (default), False = sin
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
                     windowSize=HPCP_WEIGHT_WINDOW_SIZE,
                     maxShifted=HPCP_SHIFT)
    key = estd.KeyEDM(pcpSize=HPCP_SIZE, profileType=KEY_PROFILE)
    audio = loader()
    duration = len(audio)
    frame_start = 0
    chroma = []
    if SKIP_FIRST_MINUTE and duration > (SAMPLE_RATE * 60):
        audio = audio[SAMPLE_RATE * 60:]
        duration = len(audio)
    if FIRST_N_SECS > 0:
        if duration > (FIRST_N_SECS * SAMPLE_RATE):
            audio = audio[:FIRST_N_SECS * SAMPLE_RATE]
            duration = len(audio)
    if AVOID_EDGES > 0:
        initial_sample = (AVOID_EDGES * duration) * 0.01
        final_sample = duration - initial_sample
        audio = audio[initial_sample:final_sample]
        duration = len(audio)
    while frame_start <= (duration - WINDOW_SIZE):
        spek = rfft(window(audio[frame_start:frame_start + WINDOW_SIZE]))
        if sum(spek) <= 0.00:
            frame_start += HOP_SIZE
            continue
        p1, p2 = speaks(spek)  # p1 = freqs; p2 = magnitudes
        if SPECTRAL_WHITENING:
            p2 = sw(spek, p1, p2)
        pcp = hpcp(p1, p2)
        if not DETUNING_CORRECTION or SHIFT_SCOPE == 'average':
            chroma.append(pcp)
        elif DETUNING_CORRECTION and SHIFT_SCOPE == 'frame':
            pcp = shift_pcp(pcp, HPCP_SIZE)
            chroma.append(pcp)
        else:
            raise NameError("SHIFT_SCOPE must be set to 'frame' or 'average'")
        frame_start += HOP_SIZE
    if not chroma:
        return 'Silence'
    chroma = np.sum(chroma, axis=0)
    if DETUNING_CORRECTION and SHIFT_SCOPE == 'average':
        chroma = shift_pcp(list(chroma), HPCP_SIZE)
    chroma = chroma.tolist()
    estimation = key(chroma)
    chroma = str(chroma)[1:-1]
    key = estimation[0] + ' ' + estimation[1]
    confidence = estimation[2]
    filename = soundfile[soundfile.rfind('/') + 1:soundfile.rfind('.')]
    raw_output = "{0}\t{1}\t{2:.2f}\t{3}".format(filename,
                                                 key,
                                                 confidence,
                                                 chroma)
    textfile = open(write_to + '/' + filename + '.key', 'w')
    textfile.write(raw_output)
    textfile.close()
    return key
