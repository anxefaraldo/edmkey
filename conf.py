# ===================================== #
# KEY ESTIMATION CONFIGURATION SETTINGS #
# ===================================== #

# Global
# ------
SAMPLE_RATE = 44100
AUDIO_FILE_TYPES = {'.wav', '.mp3', 'flac', '.aiff', '.ogg'}

# Faraldo
# -------
AVOID_EDGES         = 0  # % of duration at the beginning and end that is not analysed.
FIRST_N_SECS        = 0  # only analyse the first N seconds of each track (o = full track)
SKIP_FIRST_MINUTE   = False
SPECTRAL_WHITENING  = True
DETUNING_CORRECTION = True
SHIFT_SCOPE         = 'average'  # ['average', 'frame']

# FFT
# ---
WINDOW_SIZE = 4096
HOP_SIZE    = 4 * WINDOW_SIZE
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
HPCP_SIZE               = 36
HPCP_WEIGHT_WINDOW_SIZE = 1  # semitones
HPCP_WEIGHT_TYPE        = 'cosine'   # ['none', 'cosine', 'squaredCosine']

# Key Detector
# ------------
KEY_PROFILE              = 'edma'

""" 
Key Profiles:
- 'Diatonic' - binary profile with diatonic notes of both modes. Could be useful for ambient music or diatonic music
   which is not strictly 'tonal fuctional'.
- 'Tonic Triad' - just the notes of the major and minor chords. Exclusively for testing.
- 'Krumhansl' - reference key profiles after cognitive experiments with users. They should work generally fine for 
   pop music.
- 'Temperley' - key profiles extracted from corpus analysis of euroclassical music. Therefore, they perform best on
   this repertoire (especially in minor).
- 'Shaath' -  profiles based on Krumhansl's specifically tuned to popular and electronic music.
- 'Noland' - profiles from Bach's 'Well Tempered Klavier'.
- 'edma' - automatic profiles extracted from corpus analysis of electronic dance music [3]. They normally perform
   better that Shaath's.
- 'edmm' - automatic profiles extracted from corpus analysis of electronic dance music and manually tweaked according
   to heuristic observation. It will report major modes (which are poorly represented in EDM) as minor, but improve 
   performance otherwise [3]."""
