from .. import config 
import numpy as np
import matplotlib.pyplot as plt
import itertools
import logging, sys
#from ..Defuzzifier.defuzzifier  import Defuzzifier

class Output:
    def __init__(self, fuzzy_output, universe=None):
        self._outputs = fuzzy_output
        #self._universe = universe
    
    def get_array(self):
        return self._outputs
        
    @staticmethod
    def output_toDict(output):
        G = {}
        for rule_output in output:
            d = dict(rule_output)
            for k,v in d.items():
                if not k in G:
                    G[k]= []
                G[k].append(v)
        return G


    def get_outputs(self):
        return Output.output_toDict(self._outputs).keys()
    
    # def get_points(self, name):
    #     if not name in self.get_outputs():
    #         logging.error('get_points: variable name does not exist in output')
    #         return None
    #     return len(self.values(name))
    
    # def universe(self, name, range=None):
    #     if not name in self.get_outputs():
    #         logging.error('universe: variable name does not exist in output')
    #         return None
    #     if not range:
    #         return self._universe[name]
    #     elif range=='inf':
    #         return self._universe[name][0]
    #     elif range=='sup':
    #         return self._universe[name][1]
    #     elif range=='list':
    #         return np.linspace(self.universe(name, 'inf'), self.universe(name, 'sup'), num=self.get_points(name), endpoint=True, retstep=False, dtype=None)
    
    # def values(self, name):
    #     if not name in self.get_outputs():
    #         logging.error('values: variable name does not exist in output')
    #         return None
    #     return self._outputs[name]

    def show(self, defuzzifier=None):
        i = 1
        u = None
        i = 1
        consequents = Output.output_toDict(self._outputs)
        for key in self.get_outputs():
            universe = consequents[key][0].universe
            plt.subplot(len(self.get_outputs()), 1, i)
            if i==1:
                plt.title('Outputs', size=18)
            i = i+1
            plt.ylabel(key, size=18)
            u = np.linspace(universe[0], universe[1], num=config.default_points, endpoint=True, retstep=False, dtype=None)
            for G in consequents[key]:
                plt.fill_between(u, G.eval(u), 0, label=G.name)
                if defuzzifier is not None:
                    if isinstance(defuzzifier, (list,)):
                        for i,d in enumerate(defuzzifier):
                            crisp = d(self).eval()[key]
                            plt.axvline(x=crisp, color='black', lw=4)
                            plt.annotate(d.name, xy=(crisp, 0.3+i*0.1), xytext=(u[-10], 0.5+i*0.1),
                                    arrowprops=dict(facecolor='black', shrink=0.05), size=12)
                    else:
                        crisp = defuzzifier(self).eval()[key]
                        plt.axvline(x=crisp, color='black', lw=4)
                        plt.annotate(defuzzifier.name, xy=(crisp, .5), xytext=(u[-10], 0.7),
                                arrowprops=dict(facecolor='black', shrink=0.05), size=18)
                plt.grid()                
        plt.xlabel('Universe')
        plt.show()
    
    def __str__(self):
        return "Outputs: {}".format([str(name) for name in list(self.get_outputs())])