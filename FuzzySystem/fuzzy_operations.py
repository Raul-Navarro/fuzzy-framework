# Copyright (c) 2020 Raul Navarro-Almanza,
#   Universidad Autónoma de Baja California
#
# SPDX-License-Identifier: MIT
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import numpy as np


def algebraic_sum(x, y=None):
    '''Performs algebraic sum between x and y, or x if y is None

    :param x: [array] values
    :param y: [array, optional] values
    :return: array of values. x + y - x*y
    '''
    if y is not None:
        if not isinstance(x, (list,)):
            x = [x]
        if not isinstance(y, (list,)):
            y = [y]
        if len(x) == len(y):
            return [xi + yi - xi * yi for xi, yi in zip(x, y)]
    else:
        x = np.array(x)
        if x.ndim > 1:
            r = np.zeros([x.shape[1]])
            for i in range(x.shape[0]):
                r = r + x[i, :] - r * x[i, :]
            return r
        else:
            r = 0
            for i in range(len(x)):
                r = r + x[i] - r * x[i]
            return r


def algebraic_prod(x, y=None):
    '''Performs algebraic product between x and y, or x if y is None

        :param x: [array] values
        :param y: [array, optional] values
        :return: array of values. x*y
    '''
    if y is not None:
        if not isinstance(x, (list,)):
            x = [x]
        if not isinstance(y, (list,)):
            y = [y]
        if len(x) == len(y):
            return [xi * yi for xi, yi in zip(x, y)]
    else:
        x = np.array(x)
        if x.ndim > 1:
            return np.prod(np.array(x), axis=0)
        else:
            return np.prod(np.array(x))


def maximum(x, y=None):
    '''Performs the maximum between x and y, or x if y is None

        :param x: [array] values
        :param y: [array, optional] values
        :return: array of values. max(x,y)
    '''
    if y is not None:
        if not isinstance(x, (list, np.ndarray,)):
            x = [x]
        if not isinstance(y, (list, np.ndarray,)):
            y = [y]
        if len(x) == len(y):
            return np.maximum(x, y)
        raise Exception('X and Y have different lenghts')
    else:
        x = np.array(x)
        if x.ndim > 1:
            return np.max(np.array(x), axis=0)
        else:
            return np.max(np.array(x))


def minimum(x, y=None):
    '''Performs the minimum between x and y, or x if y is None

        :param x: [array] values
        :param y: [array, optional] values
        :return: array of values. min(x,y)
    '''
    if y is not None:
        if not isinstance(x, (list, np.ndarray,)):
            x = [x]
        if not isinstance(y, (list, np.ndarray,)):
            y = [y]
        if len(x) == len(y):
            return np.minimum(x, y)
        raise Exception('X and Y have different lenghts')
    else:
        x = np.array(x)
        if x.ndim > 1:
            return np.min(np.array(x), axis=0)
        else:
            return np.min(np.array(x))


def union(x, y, type='max'):
    '''Performs union between x and y

        :param x: [array] values
        :param y: [array] values
        :param type: [str] union operator. "max" or "sum"
        :return: array of values
    '''
    if type == 'max':
        return np.squeeze(maximum(x, y))
    elif type == 'sum':
        return np.squeeze(algebraic_sum(x, y))
    else:
        raise Exception("Union only by 'max' or 'sum'")


def intersection(x, y, type='min'):
    '''Performs intersection between x and y

            :param x: [array] values
            :param y: [array] values
            :param type: [str] union operator. "min" or "prod"
            :return: array of values
    '''
    if type == 'min':
        return np.squeeze(minimum(x, y))
    elif type == 'prod':
        return np.squeeze(algebraic_prod(x, y))
    else:
        raise Exception("Intersection only by 'min' or 'prod'")
