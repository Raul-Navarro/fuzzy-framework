"""A python framework to build Fuzzy Inference Systems

Raul Navarro-Almanza<rnavarro@uabc.edu.mx>
"""

from FuzzySystem.fuzzyrule import TSKConsequent, Aggregation, FuzzyRule, Antecedent, Consequent
from FuzzySystem.output import Output
from FuzzySystem import config, fuzzyvariable


class FuzzyInferenceSystem:
    '''Class to perform the inference process using fuzzy logic

        :param rules: List of rules to conform the knowledge base
        :param points: Number of points to perform the evaluation
        :param inputs: dictionary of inputs
        :param outputs: dictionary of outputs
        :param and_op: Conjunction operator
        :param or_op: Union operator
        :param verbose: flag to print information
        '''

    def __init__(self,
                 rules,
                 points=config.default_points,
                 inputs=None,
                 outputs=None,
                 and_op='min',
                 or_op='max',
                 verbose=False):
        self.and_op = and_op
        self.or_op = or_op
        self.type = None
        self.all_inputs = inputs
        self.all_outputs = outputs
        self.rules = rules
        self.verbose = verbose

        if rules is not None:
            for r in rules:
                if isinstance(r.consequent, (TSKConsequent, )):
                    if self.type == 'Mamdani':
                        raise Exception(
                            'The FIS must has only one type of Consequent')
                    else:
                        self.type = 'Sugeno'
                elif isinstance(r.consequent, (Consequent, )):
                    if self.type == 'Sugeno':
                        raise Exception(
                            'The FIS must has only one type of Consequent')
                    else:
                        self.type = 'Mamdani'
                else:
                    raise Exception('Not recognized consequent type: ',
                                    type(r.consequent))

        self.points = points

        if rules:
            if isinstance(rules, (list, )):
                self.rules = rules
            else:
                self.rules = [rules]

    def add_rule(self, rule):
        '''Add a rule to the existing knowledge base

        :param rule: The rule to append to the system
        :type rule: FuzzyRule
        '''
        if isinstance(rule, (FuzzyRule,)):
            self.rules.append(rule)

    def show_rules(self):
        '''Shows in natural language the knowledge base'''
        print("\nFuzzy System Rules:")
        for r in self.rules:
            print(str(r))

    def eval(self, inputs, verbose=None):
        '''Evaluates the fuzzy inference system

        :param inputs: Inputs to evaluate.
        :type inputs: number, list, pandas data frame
        :param verbose: flog to print information
        :return: Output object that contains the fuzzy set of the evaluated consequent
        '''
        if verbose is None:
            verbose = self.verbose

        from .utils import format_inputs
        inputs = format_inputs(inputs, inputs=self.inputs, verbose=verbose)

        return Output([
            rule.eval(
                inputs, and_op=self.and_op, or_op=self.or_op, verbose=verbose)
            for rule in self.rules
        ],
                      type=self.type)

    @property
    def inputs(self):
        '''Dictionary with the system's inputs'''
        input = {}
        if self.all_inputs:
            for fvar in self.all_inputs:
                input[fvar.name] = fvar
        else:
            for rule in self.rules:
                input.update(rule.inputs)
        return input

    @property
    def outputs(self):
        '''Dictionary with the system's outputs'''
        output = {}
        if self.all_outputs:
            if isinstance(self.all_outputs, (fuzzyvariable.FuzzyVariable,)):
                output[self.all_outputs.name] = self.all_outputs
            elif isinstance(self.all_outputs[0],
                            (fuzzyvariable.FuzzyVariable,)):
                for fvar in self.all_outputs:
                    output[fvar.name] = fvar
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
        '''Matrix with the relationships between antecedents and consequent'''
        mat = []
        for rule in self.rules:
            r_mat = []
            if isinstance(rule.antecedent, (
                    list,
                    Antecedent,
            )):
                if isinstance(rule.antecedent.propositions, (Aggregation,)):
                    r_mat = rule.antecedent.propositions.get_tuples()
                else:
                    for proposition in rule.antecedent.propositions:
                        r_mat = r_mat + [proposition.get_tuple()]
            if isinstance(rule.consequent, (
                    list,
                    Consequent,
            )):
                for proposition in rule.consequent.propositions:
                    r_mat = r_mat + [proposition.get_tuple()]
            r_mat = r_mat + [("weight", rule.weight)]
            mat.append(r_mat)
        return mat

    def get_matrix_rules(self, negatives=True):
        '''Generates the matrix with the associations in the rules

        :param negatives: If is True, the negated antecedents are multiplied by -1
        :return: Matrix with the rule associations.
        '''

        outputs_classes_id = {}
        for i, k in enumerate(self.outputs.keys()):
            fsets_names = [f.name for f in self.outputs[k].fuzzysets]
            outputs_classes_id[i] = dict(
                zip(fsets_names, range(1,
                                       len(fsets_names) + 1)))

        fuzzysets_id = {}
        for i, k in enumerate(self.inputs.keys()):
            fsets_names = [f.name for f in self.inputs[k].fuzzysets]
            fuzzysets_id[i] = dict(
                zip(fsets_names, range(1,
                                       len(fsets_names) + 1)))

        mrules = []
        for r in self.matrix_rules:
            temp = []
            d = dict(r)
            for i, k in enumerate(self.inputs.keys()):
                if k in d.keys():
                    # If the proposition has a complement operator over fuzzy set
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
            # Adding weight rule to matrix_rules
            temp = temp + [d["weight"]]
            for i, o in enumerate(self.outputs.keys()):
                temp = temp + [outputs_classes_id[i][d[o]]]
            mrules.append(temp)
        return mrules

    def get_structure(self):
        '''Create a json representation of the FIS structure

        :return: Dictionary with all the elements in the FIS
        '''
        structure = {}
        # TODO: Add all compatible membership functions to the dictionary
        name_dict = {'Gaussian mf': 'gaussmf'}
        for k in self.inputs.keys():
            structure[k] = []
            structure[k] = structure[k] + [[
                name_dict[f.mf.name], [f.name, f.mf.params, f.universe]
            ] for f in self.inputs[k].fuzzysets]
        output_list = []
        output_structure = {}
        outputs = self.outputs
        if isinstance(outputs, (dict, )):
            for k in outputs.keys():
                output_structure[k] = []
                output_structure[k] = output_structure[k] + [[
                    name_dict[f.mf.name], [f.name, f.mf.params, f.universe]
                ] for f in self.outputs[k].fuzzysets]
            return {"inputs": structure, "outputs": output_structure}

        if isinstance(outputs, (list, )):
            output_list = outputs
        elif isinstance(outputs, (fuzzyvariable.FuzzyVariable,)):
            output_list = output_list + [[
                name_dict[f.mf.name], [f.name, f.mf.params, f.universe]
            ] for f in outputs.fuzzysets]

        return {"inputs": structure, "outputs": output_list}
