# Copyright (c) 2020 Raul Navarro-Almanza,
#   Universidad Autónoma de Baja California
#
# SPDX-License-Identifier: MIT
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from .. import config
import numpy as np
import matplotlib.pyplot as plt
import itertools
import logging, sys
from ..NonSingleton.nonsingleton import NonSingleton
from ..fuzzy_operations import intersection


class FuzzySet:
    def __init__(self, name, mf, fs_operator='min'):
        self.name = name
        self.mf = mf
        self.firing_strength = None
        self.fs_operator = fs_operator

    @property
    def universe(self):
        return self.mf.universe

    @universe.setter
    def universe(self, value):
        self.mf.universe = value

    def eval(self, x, firing_strength=None, fs_operator=None):
        if fs_operator != None:
            self.fs_operator = fs_operator

        if isinstance(x, (NonSingleton, )):
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
        self.firing_strength = firing_strength
        self.fs_operator = and_op
        return self

    def __str__(self):
        info = "\nname: {0}\nmembership function: {1}\nparams: {2} \nfiring strength:{3}\n"
        return info.format(self.name, self.mf.name, self.mf.params,
                           self.firing_strength)

    def complement(self):
        self.mf.complement()
        return self

    def show(self, points=config.default_points, axes=None):
        u = np.linspace(self.mf.universe[0],
                        self.mf.universe[1],
                        num=points,
                        endpoint=True,
                        retstep=False,
                        dtype=None)
        #u = np.sort(np.concatenate([u, self.mf.params], axis=0))
        #u = np.unique(u)
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
