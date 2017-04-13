
# ======================= #
# KEY ESTIMATION SETTINGS #
# ======================= #

# File Settings
# -------------
SAMPLE_RATE                  = 44100
VALID_FILE_TYPES             = {'.wav', '.mp3', 'flac', '.aiff', '.ogg'}
RAW_OUTPUT                   = False

# Analysis Parameters
# -------------------
HIGHPASS_CUTOFF              = 0
SPECTRAL_WHITENING           = False
DETUNING_CORRECTION          = False
DETUNING_CORRECTION_SCOPE    = 'average'  # {'average', 'frame'}
PCP_THRESHOLD                = 0
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
HPCP_NON_LINEAR              = False
HPCP_NORMALIZE               = 'none'  # {none, unitSum, unitMax}
HPCP_SHIFT                   = False
HPCP_REFERENCE_HZ            = 440
HPCP_SIZE                    = 12
HPCP_WEIGHT_WINDOW_SEMITONES = 1         # semitones
HPCP_WEIGHT_TYPE             = 'cosine'  # {'none', 'cosine', 'squaredCosine'}

# Scope and Key Detector Method
# -----------------------------
AVOID_TIME_EDGES             = 0         # percentage of track-length not analysed on the edges.
FIRST_N_SECS_ONLY            = None      # analyse first n seconds of each track (0 = full track)
SKIP_N_SECS_AT_START         = 0
ANALYSIS_TYPE                = 'global'  # {'local', 'global'}
N_WINDOWS                    = 100       # if ANALYSIS_TYPE is 'local'
WINDOW_INCREMENT             = 100       # if ANALYSIS_TYPE is 'local'
KEY_PROFILE                  = 'bmtg'   # {'edma', 'edmm', 'bmtg', 'bmtg-raw'}
USE_THREE_PROFILES           = False
WITH_MODAL_DETAILS           = False