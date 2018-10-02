from .. import config 
import numpy as np
import matplotlib.pyplot as plt
import itertools
import logging, sys
from ..NonSingleton.nonsingleton import NonSingleton
from ..fuzzy_operations import intersection

class FuzzySet:
    def __init__(self, name, mf):
        self.name = name
        self.mf = mf
        self.mf.name = name
        self.firing_strength = None
        
    @property
    def universe(self):
        return self.mf.universe

    @universe.setter
    def universe(self, value):
        self.mf.universe = value
    
    def eval(self, x, firing_strength=None, fs_operator = 'min'):
        if isinstance(x, (NonSingleton,)):
            fuzzy_ns_values = intersection(self.eval(x.values), x.eval(), type=fs_operator)
            argmax = x.values[fuzzy_ns_values.argmax()]
            x = argmax

        if isinstance(x, (list,np.ndarray,)):
            if self.firing_strength is not None:
                if fs_operator=='min':
                    temp = [min(self.mf.eval(i), self.firing_strength) for i in x]
                elif fs_operator=='prod':
                    return [xi*self.firing_strength for xi in self.mf.eval(x)]
                else:
                    raise "Firing strength operator must be either 'min' or 'prod'"
                return temp
            else:
                return [self.mf.eval(i) for i in x]
        else:
            if self.firing_strength is not None:
                if fs_operator=='min':
                    return min(self.mf.eval(x), self.firing_strength)
                elif fs_operator=='prod':
                    return [xi*self.firing_strength for xi in self.mf.eval(x)]
                else:
                    raise "Firing strength operator must be either 'min' or 'prod'"
            return self.mf.eval(x)
    
    def __call__(self, x):
        return self.eval(x)
    
    def cut(self, firing_strength):
        self.firing_strength = firing_strength
        return self
    
    def __str__(self):
        info = "\nname: {0}\nmembership function: {1}\nparams: {2} \nfiring strength:{3}\n"
        return info.format(self.name, self.mf.name,self.mf.params,self.firing_strength)
    
    def show(self, points = 100):
        u = np.linspace(self.mf.universe[0], self.mf.universe[1], num=points, endpoint=True, retstep=False, dtype=None)
        c = [self.mf.eval(e) for e in u]

        fig, ax = plt.subplots()
        plt.title('Fuzzy Set')
        ax.plot(u, c, 'r-', label=self.name)
        if self.firing_strength is not None:
            ax.axhline(self.firing_strength, color='black', lw=2)
        ax.axhline(0, color='black', lw=1)
        legend = ax.legend(loc='upper left', shadow=True, fontsize='x-large')
        
        legend.get_frame().set_facecolor('#FFFFFF')
        ax.grid()
        plt.show()
