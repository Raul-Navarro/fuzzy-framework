# Copyright (c) 2020 Raul Navarro-Almanza,
#   Universidad Autónoma de Baja California
#
# SPDX-License-Identifier: MIT
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import matplotlib.pyplot as plt
import numpy as np

from FuzzySystem import config
from FuzzySystem.fuzzyrule import Proposition


class FuzzyVariable:
    ''' A class for modeling Fuzzy Variables

    :param name: Label to fuzzy variable domain
    :type name: str
    :param fuzzysets: List of fuzzy sets which the fuzzy variable can take as values
    :param universe: Range that delimits the inferior and superior domain limits.
    '''

    def __init__(self, name, fuzzysets, universe=None):
        self.name = name
        self.fuzzysets = fuzzysets

        if universe is not None:
            self.universe = universe
            for fs in self.fuzzysets:
                fs.universe = self.universe
        else:
            self.universe = self._make_universe()

    def _make_universe(self):
        inf = min([min(fs.mf.params) for fs in self.fuzzysets])
        sup = max([max(fs.mf.params) for fs in self.fuzzysets])
        return [inf, sup]

    def eval(self, x):
        ''' Evaluates the fuzzy variable given some input

        :param x: Input values
        :type x: number, list, dictionary, pandas data frame

        :return: Array of tuples with the name and evaluation of each fuzzy set [(name, eval),...]
        '''
        return [(f.name, f(x)) for f in self.fuzzysets]

    def get(self, name):
        '''Recall a fuzzy set object given a name

        :param name: name of the fuzzy set to get
        :return: FuzzySet object
        '''
        for f in self.fuzzysets:
            if f.name == name:
                return f
        return None

    def discrete_universe(self, points=config.default_points, universe=None):
        '''Creates a list of numbers between the universe limits range

        :param points: number of points to generate
        :param universe: range of the universe limits
        :return: Array of numbers in the universe
        '''
        if universe is None:
            universe = self.universe
        u = np.linspace(universe[0],
                        universe[1],
                        num=points,
                        endpoint=True,
                        retstep=False,
                        dtype=None)
        u = u.flatten()
        return u

    def show(self,
             points=config.default_points,
             axes=None,
             format_strings='-'):
        '''
        Plots all fuzzy set's membership function in the fuzzy variable

        :param points: number of samples to evaluate the membership function
        :type points: int
        :param axes: for outside plotting
        :type axes: plt.axes
        :param format_strings: line style
        '''
        u = self.discrete_universe(points)

        # members = []
        if not axes:
            fig, ax = plt.subplots()
        else:
            ax = axes
        ax.set_title(self.name)
        for fs in self.fuzzysets:
            ax.plot(u, fs.eval(u), format_strings, label=fs.name)
        # if self.firing_strength:
        #    ax.axhline(self.firing_strength, color='black', lw=2)
        ax.axhline(0, color='black', lw=1)
        ax.legend(loc='upper right',
                  fontsize='x-large',
                  fancybox=True,
                  framealpha=0.5)
        ax.grid()
        if not axes:
            plt.show()

    def __eq__(self, fsname):
        return Proposition(self, fsname)

    def __getitem__(self, fsname):
        if isinstance(fsname, (int, )) and len(self.fuzzysets) >= fsname:
            return Proposition(self, self.fuzzysets[fsname].name)

        if fsname in [f.name for f in self.fuzzysets]:
            return Proposition(self, fsname)

    def __call__(self, x):
        return self.eval(x)
