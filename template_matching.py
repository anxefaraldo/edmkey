# coding=utf-8
import numpy as np
from scipy.stats import pearsonr

# Essentia's algorithm had a function to resize pcp's to fit the key profiles
# consider implementing this in the future

# podríamos generar perfiles que, una vez extraídas sus características modales,
# maximicen la diferencia entre ellos

# it is going to be sensible as to whether we start counting on A or on C... I would suggest C, thoguh
#key_names = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
key_names = ["A", "Bb", "B", "C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab"]

key_templates = {'bgate': np.array([[1., 0.00, 0.42, 0.00, 0.53, 0.37, 0.00, 0.77, 0.00, 0.38, 0.21, 0.30],
                                    [1., 0.00, 0.36, 0.39, 0.00, 0.38, 0.00, 0.74, 0.27, 0.00, 0.42, 0.23]]),

                 'braw': np.array([[1., 0.1573, 0.4200, 0.1570, 0.5296, 0.3669, 0.1632, 0.7711, 0.1676, 0.3827, 0.2113, 0.2965],
                                   [1., 0.2330, 0.3615, 0.3905, 0.2925, 0.3777, 0.1961, 0.7425, 0.2701, 0.2161, 0.4228, 0.2272]]),

                 'diatonic': np.array([[1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
                                      [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1]]),

                 'monotonic': np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                        [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]]),

                 'triads': np.array([[1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
                                     [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]]),

                 'edma':  np.array([[1., 0.2875, 0.5020, 0.4048, 0.6050, 0.5614, 0.3205, 0.7966, 0.3159, 0.4506, 0.4202, 0.3889],
                                    [1., 0.3096, 0.4415, 0.5827, 0.3262, 0.4948, 0.2889, 0.7804, 0.4328, 0.2903, 0.5331, 0.3217]]),

                 'edmm':  np.array([[1., 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 1.0000],
                                    [1., 0.2321, 0.4415, 0.6962, 0.3262, 0.4948, 0.2889, 0.7804, 0.4328, 0.2903, 0.5331, 0.3217]]),

                 'krumhansl': np.array([[6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88],
                                        [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]]),

                 'temperley99': np.array([[5.0, 2.0, 3.5, 2.0, 4.5, 4.0, 2.0, 4.5, 2.0, 3.5, 1.5, 4.0],
                                          [5.0, 2.0, 3.5, 4.5, 2.0, 4.0, 2.0, 4.5, 3.5, 2.0, 1.5, 4.0]]),

                 'temperley05': np.array([[0.748, 0.060, 0.488, 0.082, 0.67, 0.46, 0.096, 0.715, 0.104, 0.366, 0.057, 0.4],
                                          [0.712, 0.084, 0.474, 0.618, 0.049, 0.46, 0.105, 0.747, 0.404, 0.067, 0.133, 0.33]]),

                 'temperley-essen': np.array([[0.184, 0.001, 0.155, 0.003, 0.191, 0.109, 0.005, 0.214, 0.001, 0.078, 0.004, 0.055],
                                              [0.192, 0.005, 0.149, 0.179, 0.002, 0.144, 0.002, 0.201, 0.038, 0.012, 0.053, 0.022]]),

                 'thpcp': np.array([[0.95162, 0.20742, 0.71758, 0.22007, 0.71341, 0.48841, 0.31431, 1.00000, 0.20957, 0.53657, 0.22585, 0.55363],
                                    [0.94409, 0.21742, 0.64525, 0.63229, 0.27897, 0.57709, 0.26428, 1.0000, 0.26428, 0.30633, 0.45924, 0.35929]]),

                 'shaath': np.array([[6.6, 2.0, 3.5, 2.3, 4.6, 4.0, 2.5, 5.2, 2.4, 3.7, 2.3, 3.4],
                                     [6.5, 2.7, 3.5, 5.4, 2.6, 3.5, 2.5, 5.2, 4.0, 2.7, 4.3, 3.2]]),

                 'gomez': np.array([[0.82, 0.00, 0.55, 0.00, 0.53, 0.30, 0.08, 1.00, 0.00, 0.38, 0.00, 0.47],
                                    [0.81, 0.00, 0.53, 0.54, 0.00, 0.27, 0.07, 1.00, 0.27, 0.07, 0.10, 0.36]]),

                 'noland': np.array([[0.0629, 0.0146, 0.061, 0.0121, 0.0623, 0.0414, 0.0248, 0.0631, 0.015, 0.0521, 0.0142, 0.0478],
                                     [0.0682, 0.0138, 0.0543, 0.0519, 0.0234, 0.0544, 0.0176, 0.067, 0.0349, 0.0297, 0.0401, 0.027]])
                 }


def template_matching(pcp, profile_type='bgate'):

    if (pcp.size < 12) or (pcp.size % 12 != 0):
        raise IndexError("Input PCP size is not a positive multiple of 12")

    def _select_profile_type(profile):
        try:
            return key_templates[profile]
        except KeyError:
            print("KeyError: Unsupported profile type: {}".format(profile))
            print("valid profiles are {}".format(key_templates.keys()))

    _major, _minor = _select_profile_type(profile_type)

    first_max_major  = -1
    second_max_major = -1
    key_index_major  = -1

    first_max_minor  = -1
    second_max_minor = -1
    key_index_minor  = -1


    for shift in np.arange(pcp.size):
        correlation_major = (pearsonr(pcp, np.roll(_major, shift)))[0]
        if correlation_major > first_max_major:
            second_max_major = first_max_major
            first_max_major = correlation_major
            key_index_major = shift

        correlation_minor = (pearsonr(pcp, np.roll(_minor, shift)))[0]
        if correlation_minor > first_max_minor:
            second_max_minor = first_max_minor
            first_max_minor = correlation_minor
            key_index_minor = shift


    if first_max_major >= first_max_minor:
        key_index = key_index_major
        # key_index = (key_index_major * 12) / (pcp.size + 0.5)
        scale = 'major'
        first_max = first_max_major
        second_max = second_max_major
    else:
        # key_index = (key_index_minor * 12) / (pcp.size + 0.5)
        key_index = key_index_minor
        scale = 'minor'
        first_max = first_max_minor
        second_max = second_max_minor

    if key_index < 0:
        raise IndexError("key_index smaller than zero. Could not find key.")
    else:
        first_to_second_ratio = (first_max - second_max) / first_max
        return key_names[int(key_index)], scale, first_max, first_to_second_ratio
