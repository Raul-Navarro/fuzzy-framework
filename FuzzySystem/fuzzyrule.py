# Copyright (c) 2020 Raul Navarro-Almanza,
#   Universidad Autónoma de Baja California
#
# SPDX-License-Identifier: MIT
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import copy
import numpy as np

from FuzzySystem.fuzzy_operations import minimum, maximum
from FuzzySystem.utils import get_fuzzy_operators


class Conector:
    """Conector class to evaluate aggregators

    :meta private:
    """

    def __init__(self, operator, inputs=None, and_op=minimum, or_op=maximum):
        self.operator = operator
        self.and_op, self.or_op = get_fuzzy_operators(and_op, or_op)
        if inputs is not None:
            self.inputs = inputs

    def eval(self, param1, param2):
        return self.operator(param1, param2)

    def __call__(self, param1, param2, conector=min):
        if isinstance(param1, Aggregation):
            return self(self(param1.prop1, param1.prop2, param1.conector),
                        param2, conector)
        if isinstance(param2, Aggregation):
            return self(self(param2.prop1, param2.prop2, param2.conector),
                        param1, conector)
        if isinstance(param1, Proposition):
            param1 = param1.getfuzzyset().eval(
                self.inputs[param1.fuzzyvar.name])
        if isinstance(param2, Proposition):
            param2 = param2.getfuzzyset().eval(
                self.inputs[param2.fuzzyvar.name])
        if conector == min:
            return self.and_op(param1, param2)
        else:
            return self.or_op(param1, param2)


class Proposition:
    """Proposition class to create relationships between fuzzy variables and a fuzzy set

        :meta private:
    """

    def __init__(self, fuzzyvar, fuzzyset):
        self.fuzzyvar = fuzzyvar
        self.fuzzyset = fuzzyset
        self.__complement = False

    def __getitem__(self, index):
        if index is 0:
            return self.fuzzyvar
        elif index is 1:
            return self.fuzzyset
        else:
            return None

    def __and__(self, other):
        return Aggregation(self, other, min)

    def __or__(self, other):
        return Aggregation(self, other, max)

    def __invert__(self):
        self.__complement = not self.__complement
        return self

    def add(self, other, conector):
        return Aggregation(self, other, conector)

    def getfuzzyset(self):
        result = self.fuzzyvar.get(self.fuzzyset)
        if result is not None:
            if self.__complement:
                resultcpy = copy.deepcopy(result)
                return resultcpy.complement()
            else:
                return copy.deepcopy(result)

    def __str__(self):
        if self.__complement:
            return "{} is not {}".format(self.fuzzyvar.name, self.fuzzyset)
        else:
            return "{} is {}".format(self.fuzzyvar.name, self.fuzzyset)

    def get_tuple(self):
        if self.__complement:
            fuzzyset = "not " + self.fuzzyset
        else:
            fuzzyset = self.fuzzyset
        return (self.fuzzyvar.name, fuzzyset)


class Aggregation:
    """Aggregation class to build proposition trees

        :meta private:
    """

    def __init__(self, prop1, prop2, conector):
        self.prop1 = prop1
        self.prop2 = prop2
        self.conector = conector
        self.parent = None
        self.__fuzzyvariables = None

    def __and__(self, other):
        self.parent = Aggregation(self, other, min)
        return self.parent

    def __iand__(self, other):
        self.parent = Aggregation(self, other, min)
        return self.parent

    def __or__(self, other):
        self.parent = Aggregation(self, other, max)
        return self.parent

    def __ior__(self, other):
        self.parent = Aggregation(self, other, max)
        return self.parent

    def eval(self, x, and_op=minimum, or_op=maximum):
        op = Conector(self.conector, dict(x), and_op, or_op)
        return op(self.prop1, self.prop2, self.conector)

    @property
    def fuzzy_variables(self):
        self.__fuzzyvariables = {}
        self._inorder(self)
        return self.__fuzzyvariables

    def _inorder(self, node):
        if isinstance(node, Aggregation):
            self._inorder(node.prop1)
            self._inorder(node.prop2)
        if isinstance(node, Proposition):
            if node.fuzzyvar.name not in self.__fuzzyvariables.keys():
                self.__fuzzyvariables[node.fuzzyvar.name] = node.fuzzyvar

    def get_tuples(self):
        rule = self._get_string_tuples(self).split(":")
        rule = [r for r in rule if r not in ["", " "]]
        rule = [tuple(r.split(" is ")) for r in rule]
        return rule

    def _get_string_tuples(self, node):
        if isinstance(node, Aggregation):
            if self.conector == min or self.conector == max:
                return "{}:{}".format(self._to_string(node.prop1),
                                      self._to_string(node.prop2))
            else:
                return None

    def _to_string(self, node):
        if isinstance(node, Aggregation):
            if self.conector == min:
                return "{} and {}".format(self._to_string(node.prop1),
                                          self._to_string(node.prop2))
            elif self.conector == max:
                return "{} or {}".format(self._to_string(node.prop1),
                                         self._to_string(node.prop2))
            else:
                return None

        if isinstance(node, Proposition):
            return str(node)

    def __str__(self):
        return self._to_string(self)


class Antecedent:
    '''A class to create conditional term of a IF-THEN fuzzy rule

        :param proposition: [List of proposition] the operation FuzzyVariable[fuzzy_set_name] creates a proposition.
        :param conector: [str] defines the type or logical relationship between propositions
    '''

    def __init__(self, proposition=None, conector=None):
        self.conector = conector
        if proposition is None:
            self.propositions = []
        else:
            if isinstance(proposition, (
                    list,
                    Aggregation,
            )):
                self.propositions = proposition
            else:
                self.propositions = [proposition]

    @property
    def fuzzy_variables(self):
        '''Gets the fuzzy variable in the propositions in form of dict'''
        if isinstance(self.propositions, (Aggregation,)):
            return self.propositions.fuzzy_variables
        elif isinstance(self.propositions, (list,)):
            return dict([(p.fuzzyvar.name, p.fuzzyvar)
                         for p in self.propositions])
        else:
            raise Exception(
                'Propositions must be either an array or Agregation object')

    def get(self, variable):
        '''Gets the related fuzzy set given a name of a fuzzy variable

        :param variable: [str] fuzzy variable name in the antecedent
        :return: [FuzzySet] A fuzzy set if exits
        '''
        for prop in self.propositions:
            if variable == prop[0].name:
                return prop.getfuzzyset()
        return None

    def add(self, other):
        '''Adds some proposition to the actual antecedent

        :param other: [Proposition] the proposition to add
        '''
        if isinstance(self.propositions, (list,)):
            self.propositions.append(other)
        else:
            raise Exception('Propositions must be a list to use "add" method')

    def eval(self, x, and_op='min', or_op='max'):
        '''Performs the evaluation of the antecedents

        :param x: [dict, list, pandas Data Frame] input values
        :param and_op: [str] type of disjunction operation. "min" or "prod"
        :param or_op: [str] type of conjunction operation. "max" or "sum"
        :return: [float] the antecedent firing strength
        '''
        and_op, or_op = get_fuzzy_operators(and_op, or_op)
        if isinstance(self.propositions, (Aggregation,)):
            return self.propositions.eval(x, and_op, or_op)

        if isinstance(x, (dict,)):
            x = list(zip(x.keys(), x.values()))

        if isinstance(x, (
                list,
                np.ndarray,
        )):
            result = [
                self.get(variable).eval(value) for variable, value in x
                if self.get(variable)
            ]
            if self.conector is not None:
                if self.conector == "min":
                    return and_op(result)
                else:
                    return or_op(result)
            return result
        else:
            return self.get(x[0]).eval(x[1])

    def show(self):
        '''prints the antecedent in natural language'''
        print(self)

    def __str__(self):
        if isinstance(self.propositions, (list,)):
            str_conector = " "
            if self.conector is not None:
                if self.conector == "min":
                    str_conector = " and "
                else:
                    str_conector = " or "
            return str_conector.join(
                ["{}".format(str(prop)) for prop in self.propositions])
        if isinstance(self.propositions, (Aggregation,)):
            return str(self.propositions)
        return 'EMPTY'


class Consequent:
    '''A class to create consequent term of a IF-THEN fuzzy rule

            :param proposition: [List of proposition] the operation FuzzyVariable[fuzzy_set_name] creates a proposition.
    '''

    def __init__(self, proposition=None):
        if proposition is None:
            self.propositions = []
        else:
            if isinstance(proposition, (list,)):
                self.propositions = proposition
            else:
                self.propositions = [proposition]

    @property
    def fuzzy_variables(self):
        '''Gets the fuzzy variable in the propositions in form of dict'''
        return dict([(p.fuzzyvar.name, p.fuzzyvar) for p in self.propositions])

    def get(self, variable):
        '''Gets the related fuzzy set given a name of a fuzzy variable

                :param variable: [str] fuzzy variable name in the antecedent
                :return: [FuzzySet] A fuzzy set if exits
        '''
        for prop in self.propositions:
            if variable == prop[0].name:
                return prop[0].get(prop[1])
        return None

    def add(self, other):
        '''Adds some proposition to the actual consequent

            :param other: [Proposition] the proposition to add
        '''
        self.propositions.append(other)

    def eval(self, x, and_op=None):
        '''Performs the evaluation of the consequent

                :param x: [float] firing strength value
                :param and_op: [str] type of disjunction operation for the implication. "min" or "prod"
                :return: [FuzztSet] the resulted fuzzy set with a firing strength value
        '''
        result = []
        if isinstance(
                x, (float, np.float32, np.float64, int, np.int64, np.int32)):
            for prop in self.propositions:
                result.append(
                    (prop.fuzzyvar.name, prop.getfuzzyset().cut(x, and_op)))
            return result

        if isinstance(x, (
                list,
                np.ndarray,
        )):
            results = []
            for xi in x:
                result = []
                for prop in self.propositions:
                    result.append((prop.fuzzyvar.name,
                                   prop.getfuzzyset().cut(xi, and_op)))
                results.append(result)
            return results

    def __str__(self):
        if isinstance(self.propositions, (list,)):
            output = []
            for prop in self.propositions:
                if isinstance(prop, (tuple, )):
                    output.append(" {} is {} ".format(prop[0].name, prop[1]))
                elif isinstance(prop, (Proposition, )):
                    output.append(str(prop))
            if len(output) > 1:
                return ' and '.join(output)
            else:
                return output[0]

    def show(self):
        '''prints the antecedent in natural language'''
        print(self)


def linear_function(x, params):
    '''Performs the dot product between inputs and a set of coefficients

    :param x: [array] inputs
    :param params: [array] coefficients
    :return: [float] resulted dot product operation
    '''
    if isinstance(x, (
            list,
            np.ndarray,
    )) and isinstance(params, (list, np.ndarray)):
        params = np.array(params)
        x = np.array(x)
        # multiple instances
        if x.ndim == 2:
            x_ = np.ones([x.shape[0], 1])
            x_ = np.concatenate([x_, x], axis=1)
            return np.dot(x_, params)
        else:
            x_ = np.concatenate([[1], x], axis=0)
            return np.sum(x_ * params)


def constant_function(x, params):
    '''Performs a constant evaluation. Gives params value as output

    :param x: [float, array] inputs values
    :param params: [float] constant value
    :return: constant value given by params
    '''
    if not isinstance(
            params, (int, float, np.int32, np.int64, np.float32, np.float64)):
        raise ValueError('params value must be a number')
    if isinstance(x, (
            list,
            np.ndarray,
    )):
        x = np.array(x)
        # multiple instances
        if x.ndim == 2:
            return np.ones([x.shape[0]]) * params
        else:
            return params


tsk_function_dict = {'linear': linear_function, 'constant': constant_function}


class TSKConsequent:
    '''A class to design consequent models type Sugeno

        :param function: [str, callable] type of output function. "linear" or "constant"
        :param params: [array] coefficients array
        :param label: [str]  given name to the consequent
    '''

    def __init__(self, function, params=None, label=None):
        self.__build_in_func = False
        self.params = params
        self.function = function
        self.__other = None
        if isinstance(function, (str,)):
            self.function = tsk_function_dict.get(function)
            if self.function is None:
                raise ValueError(
                    "build in functions must be one of them: {}".format(
                        ', '.join(list(tsk_function_dict.keys()))))
            else:
                self.__build_in_func = True
                # if isinstance(params, (int, np.int)):
                #     self.params = np.ones([params], dtype=np.float64)
        elif isinstance(params, (list, np.ndarray)):
            self.params = params
        else:
            raise ValueError("parameters must be an array")

        if not callable(self.function):
            raise ValueError("'function' must be callable")

        if label is not None:
            self.name = label
        else:
            self.name = self.function.__name__

    def set_params(self, params):
        '''Establishes new parameters to be feed to the function

            :param params: [array] coefficients value
        '''
        if isinstance(params, (list, np.ndarray)):
            self.params = params

    def get_params(self):
        ''':return coefficients of the function'''
        return self.params

    def add(self, other):
        '''Adds some output consequent

            :param other: [TSKConsequent] the new output to add
        '''
        if isinstance(other, (TSKConsequent,)):
            if self.__other is None:
                self.__other = []
            self.__other.append(other)

    def eval(self, x):
        '''Evaluates the TSKConsequent functions

            :param x: [array, float] inputs to evaluate the TSKConsequent
            :return: resulted values of the functions evaluations
        '''
        x = np.array(list(x), dtype=np.float)
        x = x.squeeze()
        output = []
        if x.ndim > 1:
            # multiple instances
            # dim: Instances X Inputs
            x = x.T
            if self.__build_in_func:
                if self.params is None:
                    self.params = np.ones([x.shape[1] + 1, 1])
                output.append(self.function(x, self.params))
            else:
                output.append([self.function(*x_i, *self.params) for x_i in x])

        else:
            if self.__build_in_func:
                if self.params is None:
                    self.params = np.ones([len(x) + 1])
                output.append(self.function(x, self.params))
            else:
                output.append(self.function(*x, *self.params))

        if isinstance(self.__other, (list, )):
            for tsk_cons in self.__other:
                output.append(tsk_cons.eval(x))
        return np.array(output).squeeze()

    def __str__(self):
        return self.function.__name__


class FuzzyRule:
    '''A class for modeling fuzzy rules

    :param antecedent: [Antecedent] an antecedent object that conforms the rule
    :param consequent: [list of Consequent] a list of consequent objects that conforms the rule
    :param and_op: [str] type of disjunction operation. "min" or "prod"
    :param or_op: [str] type of conjunction operation. "max" or "sum"
    :param weight: [float] weight value for the rule
    '''

    def __init__(self,
                 antecedent=None,
                 consequent=None,
                 conector=None,
                 and_op='min',
                 or_op='max',
                 weight=1):

        self.antecedent = antecedent
        self.and_op = and_op
        self.or_op = or_op
        self.weight = weight

        if isinstance(consequent, (
                list,
                Consequent,
                TSKConsequent,
        )):
            self.consequent = consequent
        else:
            # Proposition class
            self.consequent = [consequent]
        self.conector = conector

    @property
    def inputs(self):
        '''Gets the list of all fuzzy variables in the antecedent

        :return: dictionary of the fuzzy variables
        '''
        return self.antecedent.fuzzy_variables

    @property
    def outputs(self):
        '''Gets the list of all fuzzy variables in the consequent

                :return: dictionary of the fuzzy variables or functions
        '''
        if isinstance(self.consequent, (Consequent,)):
            return self.consequent.fuzzy_variables
        elif isinstance(self.consequent, (TSKConsequent,)):
            return {self.consequent.name: self.consequent}

    def eval(self, x, and_op=None, or_op=None, verbose=False):
        '''Performs the implication process  in the fuzzy rule

        :param x: [float, array, dict, pandas Data Frame] input values
        :param and_op: [str] type of disjunction operation. "min" or "prod"
        :param or_op: [str] type of conjunction operation. "max" or "sum"
        :param verbose: print process information
        :return: [list of Output] outputs of the implication process
        '''
        if and_op is None:
            and_op = self.and_op
        if or_op is None:
            or_op = self.or_op
        if isinstance(x, (dict,)):
            firing_strength = self.antecedent.eval(x, and_op, or_op)
        elif isinstance(x, (np.ndarray,)):
            firing_strength = self.antecedent.eval(x, and_op, or_op)
        else:
            raise Exception('Input must be a dictionary or an array')

        if verbose:
            if isinstance(firing_strength, (list, np.ndarray)):
                firing_strength = np.array(firing_strength)
                np.set_printoptions(precision=2)
                print(' {}, fs = {} with weight = {:.2f}'.format(
                    str(self), firing_strength, self.weight))
            else:
                print(' {}, fs = {:.2f} with weight = {:.2f}'.format(
                    str(self), firing_strength, self.weight))

        if isinstance(firing_strength, (
                list,
                tuple,
                np.ndarray,
        )):
            firing_strength = [fs * self.weight for fs in firing_strength]
        else:
            firing_strength = firing_strength * self.weight

        if isinstance(self.consequent, (Consequent, )):
            if isinstance(firing_strength, (list,)):
                if len(firing_strength) == 1:
                    firing_strength = firing_strength[0]

            return self.consequent.eval(firing_strength, and_op)

        elif isinstance(self.consequent, (TSKConsequent,)):
            if isinstance(x, (dict, )):
                values = x.values()
                return self.consequent.eval(x=values), firing_strength
            else:
                raise ValueError("Inputs must be a tuple a dictionary")
        return [prop.eval(firing_strength) for prop in self.consequent]

    def __str__(self):
        if isinstance(self.consequent, (Consequent, )):
            return "IF {} THEN {}".format(
                str(self.antecedent), ' and '.join(
                    [str(cons) for cons in self.consequent.propositions]))
        if isinstance(self.consequent, (list, )):
            return "IF {} THEN {}".format(
                str(self.antecedent),
                ' and '.join([str(cons) for cons in self.consequent]))
        if isinstance(self.consequent, (TSKConsequent, )):
            return "IF {} THEN {}".format(str(self.antecedent),
                                          str(self.consequent))

    def show(self):
        '''Prints the rule in natural language'''
        print(self)
