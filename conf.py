# ======================= #
# KEY ESTIMATION SETTINGS #
# ======================= #

# Global
# ------
SAMPLE_RATE = 44100
HIGHPASS_CUTOFF = 200
AUDIO_FILE_TYPES = {'.wav', '.mp3', 'flac', '.aiff', '.ogg'}

# Faraldo
# -------
AVOID_EDGES         = 0  # % of duration at the beginning and end that is not analysed.
FIRST_N_SECS        = 30  # only analyse the first N seconds of each track (o = full track)
SKIP_FIRST_MINUTE   = False
SPECTRAL_WHITENING  = True
DETUNING_CORRECTION = True
SHIFT_SCOPE         = 'average'  # ['average', 'frame']
PCP_THRESHOLD       = 0.5

# FFT
# ---
WINDOW_SIZE = 4096
HOP_SIZE    = 1 * WINDOW_SIZE
WINDOW_TYPE = 'hann'
MIN_HZ      = 25
MAX_HZ      = 3500

# Spectral Peaks
# --------------
SPECTRAL_PEAKS_THRESHOLD = 0.0001
SPECTRAL_PEAKS_MAX       = 60

# HPCP
# ----
HPCP_BAND_PRESET        = False
HPCP_SPLIT_HZ           = 250  # if band_preset == True
HPCP_HARMONICS          = 4
HPCP_NON_LINEAR         = True
HPCP_NORMALIZE          = True
HPCP_SHIFT              = False
HPCP_REFERENCE_HZ       = 440
HPCP_SIZE               = 12
HPCP_WEIGHT_WINDOW_SIZE = 1  # semitones
HPCP_WEIGHT_TYPE        = 'cosine'   # ['none', 'cosine', 'squaredCosine']

# Key Detector
# ------------
ANALYSIS_TYPE            = 'global'  # ['local', 'global']
N_WINDOWS                = 100  # when ANALYSIS_TYPE is set to local
WINDOW_INCREMENT         = 100  # when ANALYSIS_TYPE is set to local (def 100)
KEY_PROFILE              = 'bmtg2'  # ['bmtg1', 'bmtg2', 'bmtg3', 'edma', 'edmm']
USE_THREE_PROFILES       = True
WITH_MODAL_DETAILS       = False
