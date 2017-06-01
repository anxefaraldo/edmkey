#!/usr/local/bin/python
# coding=utf-8

import os
import numpy as np
from label import name_to_class


def normalize_pcp_area(pcp):
    """
    Normalizes a pcp so that the sum of its content is 1,
    outputting a pcp with up to 3 decimal points.
    """
    pcp = np.divide(pcp, np.sum(pcp))
    new_format = []
    for item in pcp.tolist():
        new_format.append(round(item, 3))
    return new_format


def normalize_pcp_peak(pcp):
    """
    Normalizes a pcp so that the maximum value is 1,
    outputting a pcp with up to 3 decimal points.
    """
    pcp = np.multiply(pcp, (1 / np.max(pcp)))
    new_format = []
    for item in pcp:
        new_format.append(round(item, 3))
    print new_format
    return new_format


def shift_pcp(pcp, pcp_size=12):
    """
    Shifts a pcp to the nearest tempered bin.
    :type pcp: list
    :type pcp_size: int
    """
    tuning_resolution = pcp_size / 12
    max_val = np.max(pcp)
    if max_val <= [0]:
        max_val = [1]
    pcp = np.divide(pcp, max_val)
    max_val_index = np.where(pcp == 1)
    max_val_index = max_val_index[0][0] % tuning_resolution
    if max_val_index > (tuning_resolution / 2):
        shift_distance = tuning_resolution - max_val_index
    else:
        shift_distance = max_val_index
    pcp = np.roll(pcp, shift_distance)
    return pcp


def transpose_pcp(pcp, tonic, pcp_size=36):
    """
    Takes an incoming pcp (assuming its first position
    corresponds to the note A and transposes it down so that
    the tonic note corresponds to the first place in the vector.
    """
    transposed = np.roll(pcp, (pcp_size / 12.0) * ((tonic - 9) % 12) * -1)
    return transposed


def extract_median_pcp(dir_estimations, dir_annotations, pcp_size=36):
    """
    Extracts the mean profile from a list of vectors.
    """
    list_estimations = os.listdir(dir_estimations)
    accumulate_profiles = []
    for item in list_estimations:
        if '.key' in item:
            root = open(dir_annotations + '/' + item, 'r')
            root = root.readline()
            root, mode = root[:root.find(' ')], root[root.find(' ') + 1:]
            pcp = open(dir_estimations + '/' + item, 'r')
            pcp = pcp.readline()
            pcp = pcp[pcp.rfind('\t') + 1:].split(', ')
            for i in range(pcp_size):
                pcp[i] = float(pcp[i])
            pcp = transpose_pcp(pcp, name_to_class(root))
            accumulate_profiles.append(pcp)
    return np.median(accumulate_profiles, axis=0)
