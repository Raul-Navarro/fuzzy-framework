from .. import config
from ..FuzzyInferenceSystem.fuzzyrule import Proposition
from ..FuzzySet.fuzzyset import FuzzySet
import numpy as np
import matplotlib.pyplot as plt


class FuzzyVariable:
    def __init__(self, name, fuzzysets, universe = None):
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
    
    def show(self, points=config.default_points):
        #interval = (self.universe[1] - self.universe[0])/100.0
        #u = np.arange(self.universe[0], self.universe[1], interval)
        u = np.linspace(self.universe[0], self.universe[1], num=points, endpoint=True, retstep=False, dtype=None)
        members = []
        # Create plots with pre-defined labels.
        fig, ax = plt.subplots()
        ax.set_title(self.name)
        for fs in self.fuzzysets:
            ax.plot(u, [fs.eval(e) for e in u], label=fs.name)
        #if self.firing_strength:
        #    ax.axhline(self.firing_strength, color='black', lw=2)
        ax.axhline(0, color='black', lw=1)
        legend = ax.legend(loc='upper left', shadow=True, fontsize='x-large')
        # Put a nicer background color on the legend.
        legend.get_frame().set_facecolor('#FFFFFF')
        ax.grid()
        plt.show()
    
    def __eq__(self, fsname):
        return Proposition(self, fsname)
    
    def __getitem__(self, fsname):
        if isinstance(fsname, (int,)) and len(self.fuzzysets)>=fsname:
            return Proposition(self, self.fuzzysets[fsname].name)
        
        if fsname in [f.name for f in self.fuzzysets]:
            return Proposition(self, fsname)
    
    def __call__(self, x):
        return self.eval(x)
