import numpy as np


def mirex_score(est, truth):
    """
    Performs an evaluation of the key estimation
    according to the MIREX score, assigning
    - 1.0 points to correctly identified keys,
    - 0.5 points to keys at a distance of a perfect fifth,
    - 0.3 points to relative keys,
    - 0.2 points to parallel keys, and
    - 0.0 points to other types of errors.
    :param est: list with numeric values for key and mode :type str
    :param truth: list with numeric values for key and mode :type str
    """
    if est[0] == truth[0] and est[1] == truth[1]:
        points = 1.0
    elif est[0] == truth[0] and est[1] + truth[1] == 1:
        points = 0.2
    elif est[0] == (truth[0] + 7) % 12:
        points = 0.5
    elif est[0] == (truth[0] + 5) % 12:
        points = 0.5
    elif est[0] == (truth[0] + 3) % 12 and est[1] == 0 and truth[1] == 1:
        points = 0.3
    elif est[0] == (truth[0] - 3) % 12 and est[1] == 1 and truth[1] == 0:
        points = 0.3
    else:
        points = 0.0
    return points


def mirex_evaluation(list_with_weighted_results):
    """
    This function expects a list with all the weighted results
    according to the MIREX competition, returning a list with the
    results for each of these categories plus a weighted score.
    :type list_with_weighted_results: list
    """
    results = 5 * [0]
    size = float(len(list_with_weighted_results))
    if size == 0:
        raise ZeroDivisionError("Did not find any results to evaluate!")
    else:
        for f in list_with_weighted_results:
            if f == 1:
                results[0] += 1.0
            elif f == 0.5:
                results[1] += 1.0
            elif f == 0.3:
                results[2] += 1.0
            elif f == 0.2:
                results[3] += 1.0
            elif f == 0:
                results[4] += 1.0
        results = list(np.divide(results, size))
        results.append(np.mean(list_with_weighted_results))
        return results


def error_type(est, truth):
    """
    Performs a detailed evaluation of the key estimation.
    :type est: list with numeric values for key and mode
    :type truth: list with numeric values for key and mode
    """
    pc2degree = {0: 'I',
                 1: 'bII',
                 2: 'II',
                 3: 'bIII',
                 4: 'III',
                 5: 'IV',
                 6: '#IV',
                 7: 'V',
                 8: 'bVI',
                 9: 'VI',
                 10: 'bVII',
                 11: 'VII'}
    interval = (est[0] - truth[0]) % 12
    degree = pc2degree[interval]
    error_id = 2 * (interval + (est[1] * 12)) + truth[1]
    if est[1] == 1:
        degree = degree.lower()
    else:
        degree = degree.upper()
        degree = degree.replace('B', 'b')
    if truth[1] == 1:
        degree = 'i as ' + degree
    else:
        degree = 'I as ' + degree
    return error_id, degree
