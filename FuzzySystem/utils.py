# Copyright (c) 2020 Raul Navarro-Almanza,
#   Universidad Autónoma de Baja California
#
# SPDX-License-Identifier: MIT
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import pandas as pd
import numpy as np
from .fuzzy_operations import minimum, maximum, algebraic_prod, algebraic_sum

from FuzzySystem import fuzzy_operations as fo
from FuzzySystem.membership_function import MembershipFunction

sim = {'sim1': lambda x, y: np.sum(fo.intersection(x, y, type='min')) / np.sum(fo.union(x, y, type='max')),
       'sim2': lambda x, y: fo.maximum(fo.minimum(x, y)),
       'sim3': lambda x, y: np.sum(fo.intersection(x, y, type='min')) /
                            fo.maximum(np.sum(np.power(x, 2)), np.sum(np.power(y, 2)))[0],
       'sim4': lambda x, y: np.sum(fo.intersection(x, y, type='min') / fo.union(x, y, type='max')) / len(x),
       'sim5': lambda x, y: np.sum((2 * fo.intersection(x, y, type='min')) / fo.union(x, y, type='sum')) / len(x),
       'sim6': lambda x, y: 1 - fo.maximum(np.abs(x - y)),
       'sim7': lambda x, y: 1 - np.sum(np.abs(x - y)) / np.sum(np.abs(x + y)),
       'sim8': lambda x, y: 1 - np.sum(np.abs(x - y)) / len(x),
       'sim9': lambda x, y: np.sum(1 - np.abs(x - y)) / len(x),
       'sim10': lambda x, y: np.sum((x - y) * np.log((1 + x) / (1 + y)) + (y - x) * np.log((2 - x) / (2 - y))),
       'sim11': lambda x, y: 1 - (1 / (2 * np.log(2))) * np.sum(
           (x - y) * np.log((1 + x) / (1 + y)) + (y - x) * np.log((2 - x) / (2 - y))),
       'sim12': lambda x, y: 1 - np.sum(fo.maximum([fo.minimum(x, y), fo.minimum(1 - x, 1 - y)]) / \
                                        fo.maximum([fo.maximum(x, y), fo.maximum(1 - x, 1 - y)])) / len(x),
       }


def fuzzy_similarity(A, B, points=100, method='sim1'):
    '''Performs the fuzzy similarity measure between two fuzzy sets.

    :param A: Fuzzy set A
    :param B: Fuzzy set B
    :param points: number of points to evaluate each fuzzy set
    :param method: type of similitude to calculate. sim1 to sim12
    :return: value that represent their similitude
    '''
    if isinstance(A, (MembershipFunction,)):
        universe = np.linspace(*A.universe, points)
        x = A.eval(universe)
    else:
        x = A
    if isinstance(B, (MembershipFunction,)):
        universe = np.linspace(*B.universe, points)
        y = B.eval(universe)
    else:
        y = B
    if isinstance(method, (str,)):
        if method in sim.keys():
            return sim[method](x, y)
        else:
            raise Exception('{} does not exist in dict sim'.format(method))


def format_inputs(x, inputs=None, data_columns=None, verbose=False):
    '''Adapts a given input to a dictionary of input values

    :param x: input values
    :type x: number, list
    :param inputs: list of features names
    :param data_columns: list of features names from a Pandas Data Frame object
    :param verbose: if True, prints status information
    :return: Dictionary of inputs
    '''
    if isinstance(x, (np.ndarray,)):
        if data_columns is not None:
            x = dict(zip(data_columns, x.T))
        else:
            if input is not None:
                x = dict(zip(list(inputs.keys()), x.T))
            else:
                raise Exception('Inputs dictionary or list must be provided')

    elif isinstance(x, (pd.DataFrame,)):
        x = x.to_dict(orient='list')

    elif isinstance(x, (tuple,)):
        x = dict(x)

    if isinstance(x, (dict,)):
        if verbose:
            print('Inputs:')
            for k in x.keys():
                print('{}: {}'.format(k, x[k]))
        for k in x.keys():
            if isinstance(x[k], (list,)):
                x[k] = np.array(x[k])
        return x
    raise Exception('Input must be a dictionary or an array')


def get_fuzzy_operators(and_op='min', or_op='max'):
    '''Return the functions to perform the disjunction and conjunction operation

    :param and_op: type of operator. "min" or "prod"
    :param or_op: type of operator. "max" or "sum"
    :return: A list of functions to perform disjunction and conjunction, respectively
    '''
    if isinstance(and_op, (str,)):
        if and_op == 'min':
            and_op = minimum
        elif and_op == 'prod':
            and_op = algebraic_prod
        else:
            raise Exception(
                "Choose the correct operator either 'prod' or 'min'")
    if isinstance(or_op, (str,)):
        if or_op == 'max':
            or_op = maximum
        elif or_op == 'sum':
            or_op = algebraic_sum
        else:
            raise Exception(
                "Choose the correct operator either 'sum' or 'max'")
    return and_op, or_op
