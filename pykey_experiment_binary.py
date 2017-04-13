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

input_audio_file = '/Users/angelosx/Insync/datasets-key/gs/gs-mp3/272788.LOFI.mp3'


def plot_chroma(chromagram):
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(chromagram, y_axis='chroma', x_axis='time')
    plt.colorbar()
    plt.title('Chromagram')
    plt.tight_layout()

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

key_estimator = estd.KeyEDM(pcpSize=HPCP_SIZE, profileType=KEY_PROFILE)

if HIGHPASS_CUTOFF is None:
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
#chroma_cqt = librosa.feature.chroma_cqt(y=audio,
#                                         sr=SAMPLE_RATE)
#                                         C=None,
    #                                         # norm=np.inf,
#                                         hop_length=HOP_SIZE,
#                                         # fmin=None,
#                                         # threshold=0.0,
#                                         # tuning=None,
#                                         n_chroma=12,
#                                         n_octaves=7,
#                                         # window=None,
#                                         bins_per_octave=HPCP_SIZE)
#                                         cqt_mode='full')

duration = len(audio)
n_slices = duration / HOP_SIZE
chroma = np.empty([n_slices + 1, HPCP_SIZE], dtype='float32')
# lspec = librosa.stft(y=audio, n_fft=WINDOW_SIZE, hop_length=HOP_SIZE, window='hann', center=True)
lchroma = librosa.feature.chroma_stft(y=audio, sr=SAMPLE_RATE, n_fft=WINDOW_SIZE, hop_length=HOP_SIZE, tuning=None)
for slice_n in range(n_slices):
    spek = rfft(window(cut(audio)))
    p1, p2 = speaks(spek)
    if SPECTRAL_WHITENING:
        p2 = sw(spek, p1, p2)
    pcp = hpcp(p1, p2)
    if pcp.any():
        if not DETUNING_CORRECTION or DETUNING_CORRECTION_SCOPE == 'average':
            chroma[slice_n] = pcp
        elif DETUNING_CORRECTION and DETUNING_CORRECTION_SCOPE == 'frame':
            pcp = shift_pcp(pcp, HPCP_SIZE)
            chroma[slice_n] = pcp
        else:
            raise NameError("SHIFT_SCOPE must be set to 'frame' or 'average'.")
if not chroma.any():
    estimation = 'Silence\n'
    print "not chroma"
else:
    chroma = chroma.transpose()
    global_chroma = np.sum(chroma, axis=0)
    global_chroma = normalize_pcp_peak_np(global_chroma)
    if PCP_THRESHOLD != 0:
        global_chroma = pcp_gate(global_chroma, PCP_THRESHOLD)
    if DETUNING_CORRECTION and DETUNING_CORRECTION_SCOPE == 'average':
        global_chroma = shift_pcp(global_chroma, HPCP_SIZE) # before we had to convert 'chroma' to regular list.
    #    global_chroma = essentia.array(global_chroma) # we keed this to use essentia's Key estimator until we port ours to python
    # estimation = key_estimator(essentia.array(global_chroma))

# print(estimation)

