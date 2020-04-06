from .. import config 
import numpy as np
import matplotlib.pyplot as plt
import itertools
import logging, sys
#from ..Defuzzifier.defuzzifier  import Defuzzifier

class Output:
    def __init__(self, fuzzy_output, universe=None, type='Mamdani'):
        self.type = type
        self.multiple_outputs = False
        if self.type == 'Sugeno':
            self._outputs, self.firing_strength = zip(*fuzzy_output)
            self.firing_strength = np.squeeze(np.array(self.firing_strength))
            self._outputs = np.array(self._outputs)
        elif self.type == 'Mamdani':
            self._outputs = fuzzy_output
            if not np.array(self._outputs).ndim == 3:
                self.multiple_outputs = True
        else:
            print("Unknown Fuzzy Type System")
    
    def get_array(self, nout = 0):
        if self.multiple_outputs:
            return [output[nout] for output in np.array(self._outputs)]
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


    def get_outputs(self, nout = 0):
        if self.type == 'Mamdani':
            if self.multiple_outputs:
                temp = [output[nout] for output in np.array(self._outputs)]
                return Output.output_toDict(temp).keys()
            return Output.output_toDict(self._outputs).keys()
        elif self.type == 'Sugeno':
            return self.get_array()
    

    def show(self, defuzzifier=None, points=config.default_points, axes = None, label = True, nout = 0):
        if self.type=='Sugeno':
            return None
            
        u = None
        i = 1
        selected_output = self._outputs
        if self.multiple_outputs:
            selected_output = [output[nout] for output in np.array(self._outputs)]
        consequents = Output.output_toDict(selected_output)
        for key in self.get_outputs():
            universe = consequents[key][0].universe
            #plt.subplot()#len(self.get_outputs()), 1, i)
            if not axes:
                fig, ax = plt.subplots()
            else:
                ax = axes
            if i==1:
                ax.set_title('Output', size=14)
            i = i+1
            ax.set_ylabel(key, size=14)
            u = np.linspace(universe[0], universe[1], num=points, endpoint=True, retstep=False, dtype=None)
            for G in consequents[key]:
                ax.fill_between(u, G.eval(u), 0, label=G.name, alpha=0.85)
                if defuzzifier is not None:
                    if isinstance(defuzzifier, (list,)):
                        for i,d in enumerate(defuzzifier):
                            crisp = d(self).eval()[key]
                            ax.axvline(x=crisp,  lw=2)
                            if label:
                                ax.annotate("{}={:.3f}".format(d.name, crisp),xy=(crisp, 0.1+i*0.1), 
                                        xytext=(universe[1]+3, 0.1+i*0.1),
                                        arrowprops=dict(arrowstyle="->"), size=14, family='sans-serif')
                    else:
                        crisp = defuzzifier(self).eval()[key]
                        ax.axvline(x=crisp, lw=2)
                        if label:
                            ax.annotate("{}={:.3f}".format(defuzzifier.name, crisp), xy=(crisp, .5), xytext=(u[-10], 0.7),
                                    arrowprops=dict(arrowstyle="->",connectionstyle="arc3"), size=14)
                ax.grid()                
        ax.set_xlabel('Universe')
        if not axes:
            plt.show()
    
    def __str__(self):
        return "Outputs: {}".format([str(name) for name in list(self.get_outputs())])
