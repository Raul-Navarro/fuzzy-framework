from .. import config 
import numpy as np
import matplotlib.pyplot as plt
import itertools
import logging, sys
#from ..Defuzzifier.defuzzifier  import Defuzzifier

class Output:
    def __init__(self, fuzzy_output, universe=None, type='Mamdani'):
        self.type = type

        if self.type == 'Sugeno':
            self._outputs, self.firing_strength = zip(*fuzzy_output)
            self.firing_strength = np.squeeze(np.array(self.firing_strength))
            self._outputs = np.array(self._outputs)
        else:
            self._outputs = fuzzy_output
    
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
        if self.type == 'Mamdani':
            return Output.output_toDict(self._outputs).keys()
        elif self.type == 'Sugeno':
            return self.get_array()
    

    def show(self, defuzzifier=None):
        if self.type=='Sugeno':
            return None
            
        u = None
        i = 1
        consequents = Output.output_toDict(self._outputs)
        for key in self.get_outputs():
            universe = consequents[key][0].universe
            plt.subplot(len(self.get_outputs()), 1, i)
            if i==1:
                plt.title('Output', size=14)
            i = i+1
            plt.ylabel(key, size=14)
            u = np.linspace(universe[0], universe[1], num=config.default_points, endpoint=True, retstep=False, dtype=None)
            for G in consequents[key]:
                plt.fill_between(u, G.eval(u), 0, label=G.name)
                if defuzzifier is not None:
                    if isinstance(defuzzifier, (list,)):
                        for i,d in enumerate(defuzzifier):
                            crisp = d(self).eval()[key]
                            plt.axvline(x=crisp,  lw=2)
                            plt.annotate("{}={:.3f}".format(d.name, crisp),xy=(crisp, 0.05+i*0.05), 
                                    xytext=(universe[1], 0.05+i*0.05),
                                    arrowprops=dict(arrowstyle="->"), size=12)
                    else:
                        crisp = defuzzifier(self).eval()[key]
                        plt.axvline(x=crisp, lw=2)
                        plt.annotate("{}={:.3f}".format(defuzzifier.name, crisp), xy=(crisp, .5), xytext=(u[-10], 0.7),
                                arrowprops=dict(arrowstyle="->",connectionstyle="arc3"), size=14)
                plt.grid()                
        plt.xlabel('Universe')
        plt.show()
    
    def __str__(self):
        return "Outputs: {}".format([str(name) for name in list(self.get_outputs())])
