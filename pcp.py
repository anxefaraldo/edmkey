#!/usr/local/bin/python
# coding=utf-8

import os
import numpy as np
from conversions import name_to_class

# def correlation(vector1, mean1, std1, vector2, mean2, std2, shift):
#     """"This is copied from the Implementation in Essentia"""
#
#     r = 0.0
#     for i in range(len(vector1)):
#         r += (vector1[i] - mean1) * (vector2[shift] - mean2)
#         print r
#     r /= std1 * std2
#     print r
#     return r
#
# import scipy
# scipy.stats.pearsonr()
#
#
# def pearsonr(x, y):
#     # x and y should have same length.
#     x = np.asarray(x)
#     y = np.asarray(y)
#     n = len(x)
#     mx = x.mean()
#     my = y.mean()
#     xm, ym = x - mx, y - my
#     r_num = np.add.reduce(xm * ym)
#     r_den = np.sqrt(_sum_of_squares(xm) * _sum_of_squares(ym))
#     r = r_num / r_den
#     return r
#     #
#     # # Presumably, if abs(r) > 1, then it is only some small artifact of floating
#     # # point arithmetic.
#     # r = max(min(r, 1.0), -1.0)
#     # df = n - 2
#     # if abs(r) == 1.0:
#     #     prob = 0.0
#     # else:
#     #     t_squared = r ** 2 * (df / ((1.0 - r) * (1.0 + r)))
#     #     prob = _betai(0.5 * df, 0.5, df / (df + t_squared))
#     #
#     # return r, prob
#
#
# def _sum_of_squares(a, axis=0):
#     """
#     Squares each element of the input array, and returns the sum(s) of that.
#     Parameters
#     ----------
#     a : array_like
#         Input array.
#     axis : int or None, optional
#         Axis along which to calculate. Default is 0. If None, compute over
#         the whole array `a`.
#     Returns
#     -------
#     sum_of_squares : ndarray
#         The sum along the given axis for (a**2).
#     See also
#     --------
#     _square_of_sums : The square(s) of the sum(s) (the opposite of
#     `_sum_of_squares`).
#     """
#     a, axis = _chk_asarray(a, axis)
#     return np.sum(a * a, axis)
#
#
# def _betai(a, b, x):
#     x = np.asarray(x)
#     x = np.where(x < 1.0, x, 1.0)  # if x > 1 then return 1.0
#     return scipy.special.betainc(a, b, x)
#
#
# def _chk_asarray(a, axis):
#     if axis is None:
#         a = np.ravel(a)
#         outaxis = 0
#     else:
#         a = np.asarray(a)
#         outaxis = axis
#
#     if a.ndim == 0:
#         a = np.atleast_1d(a)
#
#     return a, outaxis


def normalize_pcp_area_np(pcp):
    """
    Normalizes a pcp so that the sum of its content is 1,
    outputting a pcp with up to 3 decimal points.
    """
    pcp = np.divide(pcp, np.sum(pcp))
    new_format = []
    for item in pcp:
        new_format.append(round(item, 3))
    return np.array(new_format)


def normalize_pcp_peak_np(pcp):
    """
    Normalizes a pcp so that the maximum value is 1,
    outputting a pcp with up to 3 decimal points.
    """
    pcp = np.multiply(pcp, (1 / np.max(pcp)))
    new_format = []
    for item in pcp:
        new_format.append(round(item, 3))
    return np.array(new_format)


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
    for item in pcp.tolist():
        new_format.append(round(item, 3))
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


def transpose_pcp(pcp, tonic_pc, pcp_size=36):
    """
    Takes an incoming pcp (assuming its first position
    corresponds to the note A and transposes it down so that
    the tonic note corresponds to the first place in the vector.
    """
    transposed = np.roll(pcp, (pcp_size / 12.0) * ((tonic_pc - 9) % 12) * -1)
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


def pcp_gate(pcp, threshold):
    """
    Zeroes vector elements with values under a certain threshold.
    """
    for i in range(len(pcp)):
        if pcp[i] < threshold:
            pcp[i] = 0
    return pcp


def pcp_sort(pcp):
    """
    Returns a new vector with sorted indexes of the incoming pcp vector.
    """
    pcp = pcp[:]
    idx = []
    for i in range(len(pcp)):
        new_index = pcp.index(np.max(pcp))
        idx.append(new_index)
        pcp[new_index] = -1
    return idx
