from conf import *
import numpy as np
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
    key = estd.Key(pcpSize=HPCP_SIZE, profileType=KEY_PROFILE)
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
        return 'Silence',
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
