# Copyright (c) 2020 Raul Navarro-Almanza,
#   Universidad Autónoma de Baja California
#
# SPDX-License-Identifier: MIT
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from FuzzySystem import config
import numpy as np
#import matplotlib.pyplot as plt
#import itertools
#import logging, sys
from FuzzySystem.output import Output

output_toDict = Output.output_toDict


class Defuzzifier:
    '''Abstract class to design defuzzifiers

    :param output: [Output] an output resulted of the implication process
    :param universe: [list] range of the domain limits [min, max]
    :param samples: [int] number of samples used to calculate the defuzzification
    :param nout: [int] index of the output to defuzzify
    :param multiple_instances: [bool]  flag to define if the Output corresponds to multiple outputs
    '''

    name = "Defuzzifier"

    def __init__(self,
                 output,
                 universe=None,
                 samples=config.default_points,
                 nout=0,
                 multiple_instances=True):
        self.nout = nout
        self.multiple_instances = False
        if isinstance(output, (Output,)) or 'Output' in str(output.__class__):
            self.multiple_instances = output.multiple_outputs and multiple_instances
            self.output = output.fuzzysets
        elif isinstance(output, (
                list,
                dict,
                np.ndarray,
        )):
            self.multiple_instances = False
            self.output = output
        else:
            raise Exception(
                "Output must be a List of rules' output or an Output object")
        self.universe = universe
        self.samples = samples
        self.G = None

    def eval(self):
        '''Performs the defuzzification process

        :return: the crisp value
        '''
        if self.multiple_instances:
            return [self.compute(e) for e in self.output]
        else:
            return self.compute(self.output)

    def compute(self, fs):
        '''abstract method. Performs the defuzzification process

        :param fs: [firing strength] firing strength values
        :return: crisp values
        '''
        pass


class TSKDefuzzifier:
    '''A class to perform the weighted average of the function outputs

    :param output: [Output] the output object to perform the defuzzification
    '''

    name = "TSK Defuzzifier"
    '''Default reference name'''

    def __init__(self, output):
        self.multiple_instances = False
        if isinstance(output, (Output,)):
            if output.type == 'Sugeno':
                self.g = output.get_array()
                self.fs = output.firing_strength
            else:
                raise Exception("Output must be result of TSK Consequents")
        else:
            raise Exception(
                "Output must be a List of rules' output or an Output object")

    def eval(self):
        '''Evaluates and computes de crisp value

        :return: output crisp value
        '''
        return self.compute()

    def compute(self):
        '''Performs the weighted average between firing strength and output functions

        :meta private:
        :return: output crisp value
        '''
        self.g = np.array(self.g)
        self.fs = np.array(self.fs)
        fs_ = self.fs / self.fs.sum(axis=0)
        return np.sum(self.g * fs_, axis=0)
        # return np.sum(self.fs * self.g) / np.sum(self.fs)


class Aggregator:
    '''Class for output aggregation through the maximum

    :meta private:
    '''

    def __init__(self, fuzzySets):
        self.fuzzySets = fuzzySets

    def getSet(self, samples=config.default_points):
        universe = np.linspace(self.fuzzySets[0].universe[0],
                               self.fuzzySets[0].universe[1], samples)
        agre_set = np.zeros([len(self.fuzzySets), len(universe)])
        for i, o in enumerate(self.fuzzySets):
            agre_set[i:] = o.eval(universe)
        return np.max(agre_set, axis=0), universe


class Centroid(Defuzzifier):
    '''A class for Centroid method defuzzification'''

    name = "Centroid"
    """Defaulf reference name"""

    def compute(self, fs):
        self.G = {}
        for name, output_array in fs.items():
            m, u = Aggregator(output_array).getSet(self.samples)
            a = np.dot(m.T, u)
            b = np.sum(m)
            self.G[name] = np.divide(a, b, out=np.zeros_like(a), where=b != 0)
        return self.G


class Heights(Defuzzifier):
    '''A class for Heights method defuzzification'''

    name = "Heights"
    '''Default reference name'''

    def compute(self, fs):
        self.G = {}
        for name, output_array in fs.items():
            y_h = np.array([])
            m_b = np.array([])
            if self.universe is None:
                self.universe = np.linspace(output_array[0].universe[0],
                                            output_array[0].universe[1],
                                            self.samples)
            for g in output_array:
                t = np.array(g.eval(self.universe))
                y = np.mean(self.universe[t == np.max(t)])
                y_h = np.append(y_h, y)
                m_b = np.append(m_b, g.eval(y))
            a = np.dot(y_h.T, m_b)
            b = np.sum(m_b)
            self.G[name] = np.divide(a, b, out=np.zeros_like(a), where=b != 0)
        return self.G


class CenterOfSets(Defuzzifier):
    '''A class for Center of Sets method defuzzification'''

    name = "Center of Sets"
    '''Default reference name'''

    def compute(self, fs):
        self.G = {}
        for name, output_array in fs.items():
            y_cos = np.array([])
            fs = np.array([])
            for g in output_array:
                d = {}
                d[name] = [g]
                c = Centroid(d, samples=self.samples)
                c = c.eval()
                y_cos = np.append(y_cos, list(c.values())[0])
                fs = np.append(fs, g.firing_strength)
            a = np.dot(y_cos.T, fs)
            b = np.sum(fs)
            self.G[name] = np.divide(a, b, out=np.zeros_like(a), where=b != 0)
        return self.G


class MeanOfMaximum(Defuzzifier):
    '''A class for Mean of Maximum  method defuzzification'''

    name = "Mean Of Maximum"
    '''Default reference name'''

    def compute(self, fs):
        self.G = {}
        for name, output_array in fs.items():
            m, u = Aggregator(output_array).getSet(self.samples)
            argmax = u[m == np.max(m)]
            self.G[name] = np.sum(argmax) / len(argmax)
        return self.G


class ModifiedHeights(Defuzzifier):
    '''A class for Modified Heights method defuzzification'''

    name = "Modified Heights"
    '''Default reference name'''

    def compute(self, fs):
        self.G = {}
        for name, output_array in fs.items():
            y_h = np.array([])
            m_b = np.array([])
            if self.universe is None:
                self.universe = np.linspace(output_array[0].universe[0],
                                            output_array[0].universe[1],
                                            self.samples)
            for g in output_array:
                t = np.array(g.eval(self.universe))
                y = np.mean(self.universe[t == np.max(t)])
                y_h = np.append(y_h, y)
                m_b = np.append(m_b, np.divide(g.eval(y), g.mf.spread**2))
            a = np.dot(y_h.T, m_b)
            b = np.sum(m_b)
            self.G[name] = np.divide(a, b, out=np.zeros_like(a), where=b != 0)

        return self.G


class LastOfMaximum(Defuzzifier):
    '''A class for Last of Maximum method defuzzification'''

    name = "Least Of Maximum"
    '''Default reference name'''

    def compute(self, fs):
        self.G = {}
        for name, output_array in fs.items():
            m, u = Aggregator(output_array).getSet(self.samples)
            argmax = u[m == np.max(m)]
            self.G[name] = np.max(argmax)
        return self.G


class FirstOfMaximum(Defuzzifier):
    '''A class for First of Maximum method defuzzification'''

    name = "First Of Maximum"
    '''Default reference name'''

    def compute(self, fs):
        self.G = {}
        for name, output_array in fs.items():
            m, u = Aggregator(output_array).getSet(self.samples)
            argmax = u[m == np.max(m)]
            self.G[name] = np.min(argmax)
        return self.G
