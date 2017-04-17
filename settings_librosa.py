
# ======================= #
# KEY ESTIMATION SETTINGS #
# ======================= #

# File Settings
# -------------
SAMPLE_RATE                  = 44100
VALID_FILE_TYPES             = {'.wav', '.mp3', 'flac', '.aiff', '.ogg'}

# Analysis Parameters
# -------------------
DETUNING_CORRECTION          = False
PCP_THRESHOLD                = 0.2
WINDOW_SIZE                  = 4096
HOP_SIZE                     = 4096
WINDOW_SHAPE                 = 'hann'
MIN_HZ                       = 25
MAX_HZ                       = 3500
HPCP_SIZE                    = 12
HPCP_WEIGHT_WINDOW_SEMITONES = 1         # semitones
HPCP_WEIGHT_TYPE             = 'cosine'  # {'none', 'cosine', 'squaredCosine'}

# Scope and Key Detector Method
# -----------------------------
FIRST_N_SECS_ONLY            = None  # analyse first n seconds of each track (0 = full track)
SKIP_N_SECS_AT_START         = 0
ANALYSIS_TYPE                = 'global'  # {'local', 'global'}
N_WINDOWS                    = 100       # if ANALYSIS_TYPE is 'local'
WINDOW_INCREMENT             = 100       # if ANALYSIS_TYPE is 'local'
KEY_PROFILE = 'bgate'  # {'bgate', 'braw', 'edma', 'edmm'}
USE_THREE_PROFILES           = True
WITH_MODAL_DETAILS           = True
