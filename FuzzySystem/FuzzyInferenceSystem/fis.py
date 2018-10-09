from .. import config
import numpy as np
import matplotlib.pyplot as plt
import itertools
import logging, sys
from .output import Output
from .fuzzyrule import TSKConsequent
from ..fuzzy_operations import algebraic_sum, algebraic_prod, minimum, maximum

class FuzzyInferenceSystem:
    def __init__(self, rules, points=config.default_points, defuzzifier=None,
                inputs=None, outputs=None, and_op=minimum, or_op=maximum):
        
        self.and_op = None
        self.or_op = None

        self.type='Mamdani'
        for r in rules:
            if isinstance(r.consequent, (TSKConsequent,)):
                self.type = 'Sugeno'
            else:
                if self.type=='Sugeno':
                    raise Exception('The FIS must has only one type of Consequent')

        if isinstance(and_op, (str,)):
            if and_op == 'min':
                self.and_op = minimum
            elif and_op == 'prod':
                self.and_op = algebraic_prod
            else:
                raise "Choose the correct operator either 'prod' or 'min'"

        if isinstance(or_op, (str,)):
            if or_op == 'max':
                self.or_op = maximum
            elif or_op == 'sum':
                self.or_op = algebraic_sum
            else:
                raise "Choose the correct operator either 'sum' or 'max'"
        
        if not self.and_op:
            self.and_op = and_op

        if not self.or_op:
            self.or_op = or_op

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
        print('\nEvaluation of FIS with inputs:')
        if isinstance(inputs, (tuple,)):
            for t in inputs:
                print(t)
        elif isinstance(inputs, (dict,)):     
            for k in inputs.keys():
                print('{}: {}'.format(k, inputs[k]))
        return Output([rule.eval(inputs, and_op=self.and_op, or_op=self.or_op) for rule in self.rules], type=self.type)
    
    @property
    def inputs(self):
        input = {}
        for rule in self.rules:
            input.update(rule.inputs)
        return input

    @property
    def outputs(self):
        output = {}
        for rule in self.rules:
            output.update(rule.outputs)
        return output

    def get_structure(self):
        pass
    
    # def _discretize(self, universe):
    #     u = np.linspace(universe[0], universe[1], num=self.points, endpoint=True, retstep=False, dtype=None)
    #     return u
    
    # def _agregation(self, outputs):
    #     fuzzy_output = {}
    #     universe = {}
    #     for output_rule in outputs:
    #         if len(output_rule)>1 and not isinstance(output_rule[0], (tuple,)):
    #             output_rule = list(itertools.chain.from_iterable(output_rule))
    #         output_rule = dict(output_rule)
    #         for key in output_rule.keys():
    #             if not key in fuzzy_output.keys():
    #                 fuzzy_output[key] = []
    #                 universe[key] = output_rule[key].universe
    #             fuzzy_output[key].append(output_rule[key].eval(self._discretize(universe[key]),
    #                                                           float(output_rule[key].firing_strength))) 
    #     for key in fuzzy_output.keys():
    #         fuzzy_output[key] = np.amax(fuzzy_output[key], axis=0)
    #     return Output(fuzzy_output, universe)
