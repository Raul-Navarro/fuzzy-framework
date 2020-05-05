# Copyright (c) 2020 Raul Navarro-Almanza,
#   Universidad Autónoma de Baja California
#
# SPDX-License-Identifier: MIT
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import numpy as np


def algebraic_sum(x, y=None):
    if y is not None:
        if not isinstance(x, (list, )):
            x = [x]
        if not isinstance(y, (list, )):
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
    if y is not None:
        if not isinstance(x, (list, )):
            x = [x]
        if not isinstance(y, (list, )):
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
    if y is not None:
        if not isinstance(x, (list, )):
            x = [x]
        if not isinstance(y, (list, )):
            y = [y]
        if len(x) == len(y):
            return np.maximum(x, y)
    else:
        x = np.array(x)
        if x.ndim > 1:
            return np.max(np.array(x), axis=0)
        else:
            return np.max(np.array(x))


def minimum(x, y=None):
    if y is not None:
        if not isinstance(x, (list, )):
            x = [x]
        if not isinstance(y, (list, )):
            y = [y]
        if len(x) == len(y):
            return np.minimum(x, y)
    else:
        x = np.array(x)
        if x.ndim > 1:
            return np.min(np.array(x), axis=0)
        else:
            return np.min(np.array(x))


def union(x, y, type='max'):
    if type == 'max':
        return np.squeeze(maximum(x, y))
    elif type == 'sum':
        return np.squeeze(algebraic_sum(x, y))
    else:
        raise Exception("Union only by 'max' or 'sum'")


def intersection(x, y, type='min'):
    if type == 'min':
        return np.squeeze(minimum(x, y))
    elif type == 'prod':
        return np.squeeze(algebraic_prod(x, y))
    else:
        raise Exception("Intersection only by 'min' or 'prod'")
