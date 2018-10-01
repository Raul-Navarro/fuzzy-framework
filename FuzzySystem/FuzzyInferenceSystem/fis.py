from .. import config
import numpy as np
import matplotlib.pyplot as plt
import itertools
import logging, sys
from .output import Output


class FuzzyInferenceSystem:
    def __init__(self, rules, points=config.default_points, defuzzifier=None,
                inputs=None, outputs=None):
        self.points = points
        if rules: 
            if isinstance(rules, (list,)):
                self.rules = rules
            else:
                self.rules = [rules]
        if inputs is not None:
            self.inputs = inputs
        if outputs is not None:
            self.outputs = outputs
            
    def show_rules(self):
        print("\nFuzzy System Rules:")
        for r in self.rules:
            print(str(r))
        
    def eval(self, inputs):
        print('\nEvaluation of fis with inputs:\n{}\n'.format(inputs))
        return self._agregation([rule.eval(inputs) for rule in self.rules])
    
    def _discretize(self, universe):
        #interval = (universe[1] - universe[0])/100.0
        #u = np.arange(universe[0], universe[1], interval)
        u = np.linspace(universe[0], universe[1], num=self.points, endpoint=True, retstep=False, dtype=None)
        return u
    
    def _agregation(self, outputs):
        fuzzy_output = {}
        universe = {}
        #logging.debug("Debug: FIS: outputs:", outputs)
        for output_rule in outputs:
            if len(output_rule)>1 and not isinstance(output_rule[0], (tuple,)):
                output_rule = list(itertools.chain.from_iterable(output_rule))
            #logging.debug("Debug: (squeeze) FIS: outputs:", outputs)
            output_rule = dict(output_rule)
            #logging.debug("Debug: FIS: rule keys:", output_rule.keys())
            for key in output_rule.keys():
                if not key in fuzzy_output.keys():
                    fuzzy_output[key] = []
                    universe[key] = output_rule[key].universe
                    #logging.debug("Debug: FIS: Universe: ", universe[key])
                #logging.debug("Debug: FIS: Rule evaluation: ", output_rule[key])
                #output_rule[key].show()
                #logging.debug("Debug: FIS: Universe: ", self._discretize(universe[key]))
                #logging.debug("Debug: FIS FS evaluation:", output_rule[key].eval(self._discretize(universe[key])))
                fuzzy_output[key].append(output_rule[key].eval(self._discretize(universe[key]),
                                                              float(output_rule[key].firing_strength))) 
        #logging.debug("Debug: FIS: _agregation fuzzy_output: ", fuzzy_output)
        for key in fuzzy_output.keys():
            fuzzy_output[key] = np.amax(fuzzy_output[key], axis=0)
        return Output(fuzzy_output, universe)
