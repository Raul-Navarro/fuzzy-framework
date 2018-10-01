from .. import config 
import numpy as np
import matplotlib.pyplot as plt
import itertools
import logging, sys


class Output:
    def __init__(self, fuzzy_output, universe):
        self._outputs = fuzzy_output
        self._universe = universe
        
    def get_outputs(self):
        return self._outputs.keys()
    
    def get_points(self, name):
        if not name in self.get_outputs():
            logging.error('get_points: variable name does not exist in output')
            return None
        return len(self.values(name))
    
    def universe(self, name, range=None):
        if not name in self.get_outputs():
            logging.error('universe: variable name does not exist in output')
            return None
        
        if not range:
            return self._universe[name]
        elif range=='inf':
            return self._universe[name][0]
        elif range=='sup':
            return self._universe[name][1]
        elif range=='list':
            return np.linspace(self.universe(name, 'inf'), self.universe(name, 'sup'), num=self.get_points(name), endpoint=True, retstep=False, dtype=None)
    
    def values(self, name):
        if not name in self.get_outputs():
            logging.error('values: variable name does not exist in output')
            return None
        return self._outputs[name]
    
    def show(self, defuzzifier=None):
        i = 1
        ###
        #fig, ax = plt.subplots()
        u = None
        i = 1
        for key in self.get_outputs():
            plt.subplot(len(self.get_outputs()), 1, i)
            if i==1:
                plt.title('Outputs', size=18)
            i = i+1
            #plt.plot(x1, y1, 'o-')
            #plt.title('A tale of 2 subplots')
            plt.ylabel(key, size=18)
            #interval = (result[1][key][1] - result[1][key][0])/100.0
            #u = np.arange(result[1][key][0], result[1][key][1], interval)
            u = np.linspace(self.universe(key, 'inf'), self.universe(key, 'sup'), num=config.default_points, endpoint=True, retstep=False, dtype=None)
            plt.fill(u, self.values(key), label=key)
            if defuzzifier is not None:
                crisp = defuzzifier(self).eval()[key]  #(self.values(key),u)
                plt.axvline(x=crisp, color='black', lw=4)
                plt.annotate(defuzzifier.name, xy=(crisp, .5), xytext=(u[-10], 0.7),
                        arrowprops=dict(facecolor='black', shrink=0.05), size=18,
                       )
            
            #if self.firing_strength:
            #    ax.axhline(self.firing_strength, color='black', lw=2)
            #ax.axhline(0, color='black', lw=1)
            #legend = ax.legend(loc='upper left', shadow=True, fontsize='x-large')
            # Put a nicer background color on the legend.
            #legend.get_frame().set_facecolor('#FFFFFF')
            plt.grid()                
        plt.xlabel('Universe')
        plt.show()
    
    def __str__(self):
        return "Outputs: {}".format([str(name) for name in list(self.get_outputs())])