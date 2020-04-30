from .. import config
import numpy as np
import matplotlib.pyplot as plt
import itertools
import logging, sys

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']

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
                #DIM: RULES X INSTANCES X OUTPUS X 2 (name, fuzzyset)
                self._outputs = np.array(self._outputs)
                self.multiple_outputs = True
        else:
            raise Exception("Unknown Fuzzy Type System")

    def get_array(self, nout=0):
        if self.multiple_outputs:
            return self._outputs[:, nout, :]
            #[output[nout] for output in self._outputs]
        return self._outputs

    @staticmethod
    def output_toDict(output):
        G = {}
        for rule_output in output:
            d = dict(rule_output)
            for k, v in d.items():
                if not k in G:
                    G[k] = []
                G[k].append(v)
        return G

    @property
    def fuzzysets(self):
        if self.type == 'Sugeno':
            return self.get_array()
        if self.multiple_outputs:
            result = []
            for i in range(self._outputs.shape[1]):
                G = {}
                for rule_output in self._outputs[:, i, :]:
                    d = dict(rule_output)
                    for k, v in d.items():
                        if not k in G:
                            G[k] = []
                        G[k].append(v)
                result.append(G)
            return result
        return Output.output_toDict(self._outputs)

    def get_outputs(self, nout=0):
        if self.type == 'Mamdani':
            if self.multiple_outputs:
                temp = self._outputs[:, nout, :]
                #temp = [output[nout] for output in self._outputs]
                return Output.output_toDict(temp).keys()
            return Output.output_toDict(self._outputs).keys()
        elif self.type == 'Sugeno':
            return self.get_array()

    def show(self,
             defuzzifier=None,
             points=config.default_points,
             axes=None,
             label=True,
             nout=0):
        if self.type == 'Sugeno':
            return None

        u = None
        i = 1
        selected_output = self._outputs
        if self.multiple_outputs:
            selected_output = self._outputs[:, nout, :]
            #[output[nout] for output in self._outputs]
        consequents = Output.output_toDict(selected_output)
        for key in consequents.keys():  #self.get_outputs():
            universe = consequents[key][0].universe
            if not axes:
                fig, ax = plt.subplots()
            else:
                ax = axes
            if i == 1:
                ax.set_title('Output', size=14)
            i = i + 1
            ax.set_ylabel(key, size=14)
            u = np.linspace(universe[0],
                            universe[1],
                            num=points,
                            endpoint=True,
                            retstep=False,
                            dtype=None)
            for G in consequents[key]:
                ax.fill_between(u, G.eval(u), 0,
                                alpha=0.60)  #label=G.name, alpha=0.85)
            if defuzzifier is not None:
                if isinstance(defuzzifier, (list, )):
                    for j, d in enumerate(defuzzifier):
                        crisp = d(consequents).eval()[key]
                        if crisp > universe[0] and crisp < universe[1]:
                            if label:
                                ax.axvline(x=crisp,
                                           lw=2,
                                           label="{}={:.3f}".format(
                                               d.name, crisp),
                                           c=colors[j])
                                print("{}={:.3f}".format(d.name, crisp))
                                #ax.annotate("{}={:.3f}".format(d.name, crisp),xy=(crisp, 0.1+j*0.1),
                                #        xytext=(universe[1]+3, 0.1+j*0.1),#xytext=(1, 0.1+j*0.1),
                                #        arrowprops=dict(arrowstyle="->"), size=12, family='sans-serif')
                    ax.legend()
                else:
                    crisp = defuzzifier(consequents).eval()[key]
                    if crisp > universe[0] and crisp < universe[1]:
                        ax.axvline(x=crisp, lw=2)
                        if label:
                            ax.axvline(x=crisp,
                                       lw=2,
                                       label="{}={:.3f}".format(
                                           defuzzifier.name, crisp))
                            #ax.annotate("{}={:.3f}".format(defuzzifier.name, crisp), xy=(crisp, .5), xytext=(1, 0.7),
                            #        arrowprops=dict(arrowstyle="->",connectionstyle="arc3"), size=14)
                    ax.legend()
                ax.grid()
        ax.set_xlabel('Universe')
        if not axes:
            plt.show()

    def __str__(self):
        return "Outputs: {}".format(
            [str(name) for name in list(self.get_outputs())])
