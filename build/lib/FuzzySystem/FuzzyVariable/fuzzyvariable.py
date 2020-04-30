from .. import config
from ..FuzzyInferenceSystem.fuzzyrule import Proposition
from ..FuzzySet.fuzzyset import FuzzySet
import numpy as np
import matplotlib.pyplot as plt


class FuzzyVariable:
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
        return [(f.name, f(x)) for f in self.fuzzysets]

    def get(self, name):
        for f in self.fuzzysets:
            if f.name == name:
                return f
        return None

    def discrete_universe(self, points=config.default_points, universe=None):
        if universe == None:
            universe = self.universe
        u = np.linspace(universe[0],
                        universe[1],
                        num=points,
                        endpoint=True,
                        retstep=False,
                        dtype=None)
        #supports = np.array([fs.mf.params for fs in self.fuzzysets]).flatten()
        #supports = list(set(supports) - set(np.intersect1d(supports, u)))
        #u = u[:-len(supports)]
        u = u.flatten()
        #u = np.sort(np.concatenate([u, supports], axis=0))
        return u

    def show(self,
             points=config.default_points,
             axes=None,
             format_strings='-'):
        u = self.discrete_universe(points)
        #members = []
        if not axes:
            fig, ax = plt.subplots()
        else:
            ax = axes
        ax.set_title(self.name)
        for fs in self.fuzzysets:
            ax.plot(u, [fs.eval(e) for e in u], format_strings, label=fs.name)
        #if self.firing_strength:
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
