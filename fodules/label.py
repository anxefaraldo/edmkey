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


def key_to_int(key):
    """
    Converts a key symbol (i.e. C major) type to int
    :type key: str
    """
    name2class = {'C major': 0,
                  'C# major': 1, 'Db major': 1,
                  'D major': 2,
                  'D# major': 3, 'Eb major': 3,
                  'E major': 4,
                  'F major': 5,
                  'F# major': 6, 'Gb major': 6,
                  'G major': 7,
                  'G# major': 8, 'Ab major': 8,
                  'A major': 9,
                  'A# major': 10, 'Bb major': 10,
                  'B major': 11,

                  'C minor': 12,
                  'C# minor': 13, 'Db minor': 13,
                  'D minor': 14,
                  'D# minor': 15, 'Eb minor': 15,
                  'E minor': 16,
                  'F minor': 17,
                  'F# minor': 18, 'Gb minor': 18,
                  'G minor': 19,
                  'G# minor': 20, 'Ab minor': 20,
                  'A minor': 21,
                  'A# minor': 22, 'Bb minor': 22,
                  'B minor': 23,
                  }
    return name2class[key]


def int_to_key(a_number):
    """
    Converts an int onto a key symbol with root and scale.
    :type a_number: int
    """
    name2class = {0:  'C major',
                  1:  'C# major',
                  2:  'D major',
                  3:  'Eb major',
                  4:  'E major',
                  5:  'F major',
                  6:  'F# major',
                  7:  'G major',
                  8:  'Ab major',
                  9:  'A major',
                  10: 'Bb major',
                  11: 'B major',

                  12: 'C minor',
                  13: 'C# minor',
                  14: 'D minor',
                  15: 'Eb minor',
                  16: 'E minor',
                  17: 'F minor',
                  18: 'F# minor',
                  19: 'G minor',
                  20: 'Ab minor',
                  21: 'A minor',
                  22: 'Bb minor',
                  23: 'B minor',
                  }
    return name2class[a_number]
