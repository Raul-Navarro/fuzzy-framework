# Copyright (c) 2020 Raul Navarro-Almanza,
#   Universidad Autónoma de Baja California
#
# SPDX-License-Identifier: MIT
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import matplotlib.pyplot as plt
import numpy as np

from FuzzySystem import config
from FuzzySystem.nonsingleton import NonSingleton
from FuzzySystem.fuzzy_operations import intersection


class FuzzySet:
    ''' A class for modeling Fuzzy Sets

        :param name: label assigned to the fuzzy set
        :type name: str
        :param mf: membership function to associate with the linguistic value
        :type mf: MembershipFunction
        :param fs_operator: firing strength operator. "min" or "prod"
        :type fs_operator: str
    '''

    def __init__(self, name, mf, fs_operator='min'):

        self.name = name
        self.mf = mf
        self.firing_strength = None
        self.fs_operator = fs_operator

    @property
    def universe(self):
        '''Universe range, [min, max]'''
        return self.mf.universe

    @universe.setter
    def universe(self, value):
        self.mf.universe = value

    def eval(self, x, fs_operator=None):
        '''Evaluate the fuzzy set given an input

        :param x: inputs values
        :type x: list, numpy array, dictionary or pandas data frame
        :param fs_operator: firing strength operator. "min" or "prod"
        :type fs_operator: str

        :returns: The membership function evaluation
        '''
        if not (fs_operator is None):
            self.fs_operator = fs_operator

        if isinstance(x, (NonSingleton,)):
            fuzzy_ns_values = intersection(self.eval(x.values),
                                           x.eval(),
                                           type=self.fs_operator)
            argmax = x.values[fuzzy_ns_values.argmax()]
            x = argmax

        if isinstance(x, (
                list,
                np.ndarray,
        )):
            if self.firing_strength is not None:
                if self.fs_operator == 'min':
                    return [
                        min(self.mf.eval(i), self.firing_strength) for i in x
                    ]
                elif self.fs_operator == 'prod':
                    return [
                        xi * self.firing_strength for xi in self.mf.eval(x)
                    ]
                else:
                    raise Exception(
                        "Firing strength operator must be either 'min' or 'prod', get {}"
                        .format(self.fs_operator))
            else:
                return self.mf.eval(x)
        else:
            if self.firing_strength is not None:
                if self.fs_operator == 'min':
                    return [min(self.mf.eval(x), self.firing_strength)]
                elif self.fs_operator == 'prod':
                    return [x * self.firing_strength]
                else:
                    raise Exception(
                        "Firing strength operator must be either 'min' or 'prod'"
                    )
            return self.mf.eval(x)

    def __call__(self, x):
        return self.eval(x)

    def cut(self, firing_strength, and_op=None):
        '''Establishes a firing strength value

        :param firing_strength: value in [0,1]
        :type firing_strength: float
        :param and_op: conjunction operation. "min" or "prod"
        :type and_op: str
        :return: self
        '''
        self.firing_strength = firing_strength
        self.fs_operator = and_op
        return self

    def __str__(self):
        info = "\nname: {0}\nmembership function: {1}\nparams: {2} \nfiring strength:{3}\n"
        return info.format(self.name, self.mf.name, self.mf.params,
                           self.firing_strength)

    def complement(self):
        '''Performs the complement operation to the fuzzy set

        :return: self
        '''
        self.mf.complement()
        return self

    def show(self, points=config.default_points, axes=None):
        '''
        Plots the fuzzy set's membership function

        :param points: number of samples to evaluate the membership function
        :type points: int
        :param axes: for outside plotting
        :type axes: plt.axes
        '''
        u = np.linspace(self.mf.universe[0],
                        self.mf.universe[1],
                        num=points,
                        endpoint=True,
                        retstep=False,
                        dtype=None)
        c = self.eval(u)
        if not axes:
            _, ax = plt.subplots()
        else:
            ax = axes
        plt.title('Fuzzy Set')
        ax.plot(u, c, '-', label=self.name)
        if self.firing_strength is not None:
            _fs = self.firing_strength
            self.firing_strength = None
            ax.plot(u,
                    self.eval(u),
                    '--',
                    label="{} {}".format("original", self.name),
                    alpha=0.4)
            self.firing_strength = _fs
            del _fs
            ax.axhline(self.firing_strength, color='black', lw=2, alpha=.5)
        ax.legend(loc='best',
                  fontsize='x-large',
                  fancybox=True,
                  framealpha=0.5)
        ax.grid()
        if not axes:
            plt.show()
