from .. import config
import numpy as np
import matplotlib.pyplot as plt
import itertools
import logging, sys
from .output import Output
from .fuzzyrule import TSKConsequent, Agregation, FuzzyRule, Antecedent, Consequent
from ..fuzzy_operations import algebraic_sum, algebraic_prod, minimum, maximum

class FuzzyInferenceSystem:
    def __init__(self, rules, points=config.default_points, defuzzifier=None,
                inputs=None, outputs=None, and_op=minimum, or_op=maximum):
        
        self.and_op = None
        self.or_op = None

        self.type=None
        for r in rules:
            if isinstance(r.consequent, (TSKConsequent,)):
                if self.type == 'Mamdani':
                    raise Exception('The FIS must has only one type of Consequent')
                else:
                    self.type = 'Sugeno'
            else:
                if self.type=='Sugeno':
                    raise Exception('The FIS must has only one type of Consequent')
                else: 
                    self.type = 'Mamdani'
                
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
            self.all_inputs = inputs
        if outputs is not None:
            self.all_outputs = outputs
    
    
    def add_rule(self, rule):
        if isinstance(rule, (FuzzyRule,)):
            self.rules.append(rule)

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

    @property
    def matrix_rules(self):
        mat = []
        input = self.inputs
        output = self.outputs
        for rule in self.rules:
            r_mat = []
            if isinstance(rule.antecedent, (list,Antecedent,)):
                for proposition in rule.antecedent.propositions:
                    r_mat = r_mat + [proposition.get_tuple()]
            if isinstance(rule.consequent, (list,Consequent,)):
                for proposition in rule.consequent.propositions:
                    r_mat = r_mat + [proposition.get_tuple()]
            mat.append(r_mat)
        return mat
        
    def get_matrix_rules(self):
        inputs_id = dict(zip(self.inputs.keys(),range(0, len(self.inputs.keys()))))
        outputs_id = dict(zip(self.outputs.keys(),range(0, len(self.outputs.keys()))))
    
        outputs_classes_id = {}
        for i,k in enumerate(self.outputs.keys()):
            fsets_names = [f.name for f in self.outputs[k].fuzzysets]
            outputs_classes_id[i]=dict(zip(fsets_names,range(0, len(fsets_names))))

        fuzzysets_id = {}
        for i,k in enumerate(self.inputs.keys()):
            fsets_names = [f.name for f in self.inputs[k].fuzzysets]
            fuzzysets_id[i]=dict(zip(fsets_names,range(1, len(fsets_names)+1)))
        
        mrules = []
        for r in self.matrix_rules:
            temp = []
            d = dict(r)
            for i,k in enumerate(self.inputs.keys()):
                if k in d.keys():
                    temp = temp + [fuzzysets_id[i][d[k]]]
            for i,o in enumerate(self.outputs.keys()):
                temp = temp + [outputs_classes_id[i][d[o]]]
            mrules.append(temp)
        return mrules




    def get_structure(self):
        structure = {}
        name_dict = {'Gaussian mf':'gaussmf'}
        for k in self.inputs.keys():
            structure[k] = []
            structure[k] = structure[k] + [[name_dict[f.mf.name],
                                [f.name, f.mf.params,f.universe]] for f in self.inputs[k].fuzzysets]
        return structure
    
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
