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
        return Output([rule.eval(inputs) for rule in self.rules])
    
    def _discretize(self, universe):
        u = np.linspace(universe[0], universe[1], num=self.points, endpoint=True, retstep=False, dtype=None)
        return u
    
    def _agregation(self, outputs):
        fuzzy_output = {}
        universe = {}
        for output_rule in outputs:
            if len(output_rule)>1 and not isinstance(output_rule[0], (tuple,)):
                output_rule = list(itertools.chain.from_iterable(output_rule))
            output_rule = dict(output_rule)
            for key in output_rule.keys():
                if not key in fuzzy_output.keys():
                    fuzzy_output[key] = []
                    universe[key] = output_rule[key].universe
                fuzzy_output[key].append(output_rule[key].eval(self._discretize(universe[key]),
                                                              float(output_rule[key].firing_strength))) 
        for key in fuzzy_output.keys():
            fuzzy_output[key] = np.amax(fuzzy_output[key], axis=0)
        return Output(fuzzy_output, universe)
