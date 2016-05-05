#!/usr/local/bin/python
# -*- coding: UTF-8 -*-


def name_to_class(key):
    """
    Converts a note name to its pitch-class value.
    :type key: str
    """
    name2class = {'B#': 0, 'C': 0,
                  'C#': 1, 'Db': 1,
                  'D': 2,
                  'D#': 3, 'Eb': 3,
                  'E': 4, 'Fb': 4,
                  'E#': 5, 'F': 5,
                  'F#': 6, 'Gb': 6,
                  'G': 7,
                  'G#': 8, 'Ab': 8,
                  'A': 9, 'A#': 10,
                  'Bb': 10, 'B': 11,
                  'Cb': 11,
                  'none': 12, '-': 12}
    return name2class[key]


def mode_to_num(mode):
    """
    Converts a scale type into numeric values (maj = 0, min = 1).
    :type mode: str
    """
    mode2num = {''       : 0,
                'major'  : 0,
                'minor'  : 1,
                'other'  : 2,
                'peak'   : 3,
                'flat'   : 4,
                'silence': 5}
    return mode2num[mode]


def key_to_list(key):
    """
    Converts a key (i.e. C major) type into a
    numeric list in the form [tonic, mode].
    :type key: str
    """
    key = key.split(' ')
    key[-1] = key[-1].strip()
    if len(key) == 1:
        key = [name_to_class(key[0]), 0]
    else:
        key = [name_to_class(key[0]), mode_to_num(key[1])]
    return key
