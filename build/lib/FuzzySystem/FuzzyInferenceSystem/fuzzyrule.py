import copy
from ..fuzzy_operations import algebraic_sum, algebraic_prod, minimum, maximum
from ..FuzzyVariable import fuzzyvariable as fv
from ..utils import get_fuzzy_operators
#from ..FuzzyVariable.fuzzyvariable import FuzzyVariable
import numpy as np


class Conector:
    def __init__(self, operator, inputs=None, and_op=minimum, or_op=maximum):
        self.operator = operator
        self.and_op, self.or_op = get_fuzzy_operators(and_op, or_op)
        if inputs is not None:
            self.inputs = inputs

    def eval(self, param1, param2):
        return self.operator(param1, param2)

    def __call__(self, param1, param2, conector=min):
        if isinstance(param1, Agregation):
            return self(self(param1.prop1, param1.prop2, param1.conector),
                        param2, conector)
        if isinstance(param2, Agregation):
            return self(self(param2.prop1, param2.prop2, param2.conector),
                        param1, conector)
        if isinstance(param1, Proposition):
            #OLD: param1 = param1.fuzzyvar.get(param1.fuzzyset).eval(self.inputs[param1.fuzzyvar.name])
            param1 = param1.getfuzzyset().eval(
                self.inputs[param1.fuzzyvar.name])
        if isinstance(param2, Proposition):
            #OLD: param2 = param2.fuzzyvar.get(param2.fuzzyset).eval(self.inputs[param2.fuzzyvar.name])
            param2 = param2.getfuzzyset().eval(
                self.inputs[param2.fuzzyvar.name])
        if conector == min:
            return self.and_op(param1, param2)
        else:
            return self.or_op(param1, param2)


class Proposition:
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
        return Agregation(self, other, min)

    def __or__(self, other):
        return Agregation(self, other, max)

    def __invert__(self):
        self.__complement = not self.__complement
        return self

    def add(self, other, conector):
        return Agregation(self, other, conector)

    def getfuzzyset(self):
        result = self.fuzzyvar.get(self.fuzzyset)
        if result is not None:
            if self.__complement:
                resultcpy = copy.copy(result)
                return resultcpy.complement()
            else:
                return copy.copy(result)

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


class Agregation:
    def __init__(self, prop1, prop2, conector):
        self.prop1 = prop1
        self.prop2 = prop2
        self.conector = conector
        self.parent = None
        self.__fuzzyvariables = None

    def __and__(self, other):
        self.parent = Agregation(self, other, min)
        return self.parent

    def __iand__(self, other):
        self.parent = Agregation(self, other, min)
        return self.parent

    def __or__(self, other):
        self.parent = Agregation(self, other, max)
        return self.parent

    def __ior__(self, other):
        self.parent = Agregation(self, other, max)
        return self.parent

    def eval(self, x, and_op=minimum, or_op=maximum):
        op = Conector(self.conector, dict(x), and_op, or_op)
        return op(self.prop1, self.prop2, self.conector)

    @property
    def fuzzy_variables(self):
        self.__fuzzyvariables = {}
        self._inorder(self)
        return self.__fuzzyvariables
        #return [(obj.name, obj) for obj in list(itertools.chain.from_iterable(self._inorder(self))) if isinstance(obj, (fv.FuzzyVariable))]

    def _inorder(self, node):
        if isinstance(node, Agregation):
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
        if isinstance(node, Agregation):
            if self.conector == min or self.conector == max:
                return "{}:{}".format(self._to_string(node.prop1),
                                      self._to_string(node.prop2))
            else:
                return None

    def _to_string(self, node):
        if isinstance(node, Agregation):
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
    def __init__(self, proposition=None, conector=None):
        self.conector = conector
        if proposition is None:
            self.propositions = []
        else:
            if isinstance(proposition, (
                    list,
                    Agregation,
            )):
                self.propositions = proposition
            else:
                self.propositions = [proposition]

    @property
    def fuzzy_variables(self):
        if isinstance(self.propositions, (Agregation, )):
            return self.propositions.fuzzy_variables
        elif isinstance(self.propositions, (list, )):
            return dict([(p.fuzzyvar.name, p.fuzzyvar)
                         for p in self.propositions])
        else:
            raise Exception(
                'Propositions must be either an array or Agregation object')

    def get(self, variable):
        for prop in self.propositions:
            if (variable == prop[0].name):
                return prop.getfuzzyset()
        return None

    def add(self, other):
        if isinstance(self.propositions, (list, )):
            self.propositions.append(other)
        else:
            raise Exception('Propositions must be a list to use "add" method')

    def eval(self, x, and_op=minimum, or_op=maximum):
        and_op, or_op = get_fuzzy_operators(and_op, or_op)
        if isinstance(self.propositions, (Agregation, )):
            return self.propositions.eval(x, and_op, or_op)

        if isinstance(x, (dict, )):
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
                if self.conector == min:
                    return and_op(result)
                else:
                    return or_op(result)
            return result
        else:
            return self.get(x[0]).eval(x[1])

    def show(self):
        print(self)

    def __str__(self):
        if isinstance(self.propositions, (list, )):
            #return ' and '.join(["{} is {}".format(var.name, value) for var, value in self.propositions])
            str_conector = " "
            if self.conector is not None:
                if self.conector == min:
                    str_conector = " and "
                else:
                    str_conector = " or "
            return str_conector.join(
                ["{}".format(str(prop)) for prop in self.propositions])
        if isinstance(self.propositions, (Agregation, )):
            return str(self.propositions)
        return 'EMPTY'


class Consequent:
    def __init__(self, proposition=None, conector=None):
        self.conector = conector
        if proposition is None:
            self.propositions = []
        else:
            if isinstance(proposition, (list, )):
                self.propositions = proposition
            else:
                self.propositions = [proposition]

    @property
    def fuzzy_variables(self):
        return dict([(p.fuzzyvar.name, p.fuzzyvar) for p in self.propositions])

    def get(self, variable):
        for prop in self.propositions:
            if (variable == prop[0].name):
                return prop[0].get(prop[1])
        return None

    def add(self, other):
        self.propositions.append(other)

    def eval(self, x, and_op=None):
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
        if isinstance(self.propositions, (list)):
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
        print(self)


class TSKConsequent():
    def __init__(self, params, function, label=None):
        if isinstance(params, (list, np.ndarray)):
            self.params = params
        else:
            raise ValueError("parameters must be an array")

        if callable(function):
            self.function = function
        else:
            raise ValueError("'function' must be callable")

        if label != None:
            self.name = label
        else:
            self.name = self.function.__name__

    def set_params(self, params):
        if isinstance(params, (list, np.ndarray)):
            self.params = params

    def get_params(self):
        return self.params

    def eval(self, x, firing_strength, and_op=algebraic_prod):
        if and_op == None:
            return self.function(*x, *self.params)
        return and_op(self.function(*x, *self.params), firing_strength)

    def __str__(self):
        return self.function.__name__


class FuzzyRule():
    def __init__(self,
                 antecedent=None,
                 consequent=None,
                 conector=None,
                 and_op=minimum,
                 or_op=maximum,
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
            #Proposition class
            self.consequent = [consequent]
        self.conector = conector

    @property
    def inputs(self):
        return self.antecedent.fuzzy_variables

    @property
    def outputs(self):
        if isinstance(self.consequent, (Consequent, )):
            return self.consequent.fuzzy_variables
        elif isinstance(self.consequent, (TSKConsequent, )):
            return {self.consequent.name: self.consequent}

    def eval(self, x, and_op=minimum, or_op=maximum, verbose=False):
        self.and_op = and_op
        self.or_op = or_op
        if isinstance(x, (dict)):
            firing_strength = self.antecedent.eval(x, self.and_op, self.or_op)
        elif isinstance(x, (np.ndarray, )):
            firing_strength = self.antecedent.eval(x, self.and_op, self.or_op)
        else:
            raise Exception('Input must be a dictionary or an array')

        if verbose:
            if isinstance(firing_strength, (list, np.ndarray)):
                firing_strength = np.array(firing_strength)
                np.set_printoptions(precision=2)
                print(' {} = {} with weight = {:.2f}'.format(
                    str(self), firing_strength, self.weight))
            else:
                print(' {} = {:.2f} with weight = {:.2f}'.format(
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
            if isinstance(firing_strength, (list)):
                if len(firing_strength) == 1:
                    firing_strength = firing_strength[0]

            return self.consequent.eval(firing_strength, self.and_op)

        elif isinstance(self.consequent, (TSKConsequent)):
            if isinstance(x, (dict, )):
                values = x.values()
                return (self.consequent.eval(x=values,
                                             firing_strength=None,
                                             and_op=None), firing_strength)
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
        print(self)
