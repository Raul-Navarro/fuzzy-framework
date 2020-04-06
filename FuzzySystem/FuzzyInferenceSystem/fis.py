from .. import config
import numpy as np
import matplotlib.pyplot as plt
import logging
from .output import Output
from .fuzzyrule import TSKConsequent, Agregation, FuzzyRule, Antecedent, Consequent
from ..FuzzyVariable import fuzzyvariable
from ..fuzzy_operations import algebraic_sum, algebraic_prod, minimum, maximum
import pandas as pd

class FuzzyInferenceSystem:
    def __init__(self, rules, points=config.default_points, defuzzifier=None,
                inputs=None, outputs=None, and_op=minimum, or_op=maximum):
        
        self.and_op = None
        self.or_op = None
        self.type=None
        self.all_inputs = inputs
        self.all_outputs = outputs
        self.rules = rules
        
        if rules is not None:
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
    
    def add_rule(self, rule):
        if isinstance(rule, (FuzzyRule,)):
            self.rules.append(rule)

    def show_rules(self):
        print("\nFuzzy System Rules:")
        for r in self.rules:
            print(str(r))
        
    def eval(self, inputs, data_columns=None):
        print('\nEvaluation of FIS with inputs:')
        if isinstance(inputs, (np.ndarray,)):
            if data_columns is not None:
                inputs = dict(zip(data_columns, inputs.T))
            else:
                inputs = dict(zip(list(self.inputs.keys()), inputs.T))
                
        if isinstance(inputs, (tuple,)):
            for t in inputs:
                print(t)

        elif isinstance(inputs, (pd.DataFrame,)):     
            inputs = inputs.to_dict(orient='list')
            for k in inputs.keys():
                print('{}: {}'.format(k, inputs[k]))

        elif isinstance(inputs, (dict,)):     
            for k in inputs.keys():
                print('{}: {}'.format(k, inputs[k]))

        return Output([rule.eval(inputs, and_op=self.and_op, or_op=self.or_op) for rule in self.rules], type=self.type)
    
    @property
    def inputs(self):
        input = {}
        if self.all_inputs:
            for fvar in self.all_inputs:
                input[fvar.name] =  fvar
        else:
            for rule in self.rules:
                input.update(rule.inputs)
        return input

    @property
    def outputs(self):
        output = {}
        if self.all_outputs:
            if isinstance(self.all_outputs, (fuzzyvariable.FuzzyVariable,)):
                output[self.all_outputs.name] = self.all_outputs
            elif isinstance(self.all_outputs[0], (fuzzyvariable.FuzzyVariable,)):
                for fvar in self.all_outputs:
                    output[fvar.name] =  fvar
            elif isinstance(self.all_outputs[0], (str,)):
                return self.all_outputs
            else:
                return output
        else:
            if self.rules:
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
                if isinstance(rule.antecedent.propositions, (Agregation,)):
                    r_mat = rule.antecedent.propositions.get_tuples()
                else:
                    for proposition in rule.antecedent.propositions:
                        r_mat = r_mat + [proposition.get_tuple()]
            if isinstance(rule.consequent, (list,Consequent,)):
                for proposition in rule.consequent.propositions:
                    r_mat = r_mat + [proposition.get_tuple()]
            r_mat = r_mat + [("weight", rule.weight)]
            mat.append(r_mat)
        return mat
    
        
    def get_matrix_rules(self, negatives=True):
        inputs_id = dict(zip(self.inputs.keys(),range(0, len(self.inputs.keys()))))
        outputs_id = dict(zip(self.outputs.keys(),range(0, len(self.outputs.keys()))))
    
        outputs_classes_id = {}
        for i,k in enumerate(self.outputs.keys()):
            fsets_names = [f.name for f in self.outputs[k].fuzzysets]
            outputs_classes_id[i]=dict(zip(fsets_names,range(1, len(fsets_names)+1)))

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
                    #If the proposition have the complement of fuzzy set
                    if "not " in d[k]:
                        name = d[k].replace("not ", "")
                        if negatives:
                            temp = temp + [-fuzzysets_id[i][name]]
                        else:
                            temp = temp + [fuzzysets_id[i][name]]
                    else:
                        temp = temp + [fuzzysets_id[i][d[k]]]
                else:
                    temp = temp + [0]
            #Add rule weight to matrix_rules
            temp = temp + [d["weight"]]
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
        output_list = []
        output_structure = {}
        outputs = self.outputs
        if isinstance(outputs, (dict,)):
            for k in outputs.keys():
                output_structure[k] = []
                output_structure[k] = output_structure[k] + [[name_dict[f.mf.name],
                                [f.name, f.mf.params,f.universe]] for f in self.outputs[k].fuzzysets]
            return {"inputs":structure, "outputs":output_structure}

        if isinstance(outputs, (list,)):
            output_list = outputs
        elif isinstance(outputs, (fuzzyvariable.FuzzyVariable,)):
            output_list = output_list + [[name_dict[f.mf.name],[f.name, f.mf.params,f.universe]] for f in outputs.fuzzysets]

        return {"inputs":structure, "outputs":output_list}
