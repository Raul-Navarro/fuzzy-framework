from .. import config 
import numpy as np
#import matplotlib.pyplot as plt
#import itertools
#import logging, sys
from ..FuzzyInferenceSystem.output import Output

output_toDict = Output.output_toDict



class Defuzzifier:
    name = "Defuzzifier"
    def __init__(self, output, universe=None, samples = 100):
        if isinstance(output, (Output,)):
            self.output = output.get_array()
        elif isinstance(output, (list,)):
            self.output = output
        else:
            raise "Output must be a List of rules' output or an Output object"
        self.universe = universe
        self.samples = samples
    
    def eval(self):
        pass

class TSKDefuzzifier:
    name = "TSK Defuzzifier"
    def __init__(self, output):
        if isinstance(output, (Output,)):
            if output.type == 'Sugeno':
                self.g = output.get_array()
                self.f = output.firing_strength
            else:
                raise Exception("Output must be result of TSK Consequents")
        else: 
            raise Exception("Output must be a List of rules' output or an Output object")
    
    def eval(self):
        return np.sum(self.f * self.g)/np.sum(self.f)

        
class Aggregator():
    def __init__(self, fuzzySets):
        self.fuzzySets = fuzzySets
        
    def getSet(self, samples=config.default_points):
        universe = np.linspace(self.fuzzySets[0].universe[0], self.fuzzySets[0].universe[1], samples)
        agre_set = np.zeros([len(self.fuzzySets), len(universe)])
        for i,o in enumerate(self.fuzzySets):
            agre_set[i:] = o.eval(universe)
        return (np.max(agre_set, axis=0), universe)

class Centroid(Defuzzifier):
    name = "Centroid"
    
    def eval(self):
        self.G = {}
        for name, output_array in output_toDict(self.output).items():
            m, u = Aggregator(output_array).getSet(self.samples)
            self.G[name] = np.dot(m.T, u)/np.sum(m)
        return self.G

class Heights(Defuzzifier):
    name = "Heights"
    
    def eval(self):
        self.G = {}
        for name, output_array in output_toDict(self.output).items():
            y_h = np.array([])
            m_b = np.array([])
            if self.universe is None:
                self.universe = np.linspace(output_array[0].universe[0], output_array[0].universe[1], self.samples)
            for g in output_array:
                t = np.array(g.eval(self.universe))
                y = np.mean(self.universe[t==np.max(t)])
                y_h = np.append(y_h,y)
                m_b = np.append(m_b, g.eval(y))
            self.G[name] = np.dot(y_h.T, m_b)/np.sum(m_b)
        return self.G
    
class CenterOfSets(Defuzzifier):
    name = "Center of Sets"
    
    def eval(self):
        self.G = {}
        for name, output_array in output_toDict(self.output).items():
            y_cos = np.array([])
            fs = np.array([])
            for g in output_array:
                c = Centroid([[(name,g)]], samples=self.samples).eval()
                y_cos = np.append(y_cos, list(c.values())[0])
                fs = np.append(fs, g.firing_strength)
            self.G[name] =  np.dot(y_cos.T, fs)/np.sum(fs)
        return self.G
    
class MeanOfMaximum(Defuzzifier):
    name = "Mean Of Maximum"
    
    def eval(self):
        self.G = {}
        for name, output_array in output_toDict(self.output).items():
            m, u = Aggregator(output_array).getSet(self.samples)
            argmax = u[m==np.max(m)]
            self.G[name] = np.sum(argmax)/len(argmax)
        return self.G
    
class ModifiedHeights(Defuzzifier):
    name = "Modified Heights"
    
    def eval(self):
        self.G = {}
        for name, output_array in output_toDict(self.output).items():
            y_h = np.array([])
            m_b = np.array([])
            if self.universe is None:
                self.universe = np.linspace(output_array[0].universe[0], output_array[0].universe[1], self.samples)
            for g in output_array:
                t = np.array(g.eval(self.universe))
                y = np.mean(self.universe[t==np.max(t)])
                y_h = np.append(y_h,y)
                m_b = np.append(m_b, np.divide(g.eval(y),g.mf.spread**2))
            self.G[name] = np.dot(y_h.T, m_b)/np.sum(m_b)
        return self.G
    
class LastOfMaximum(Defuzzifier):
    name = "Least Of Maximum"
    
    def eval(self):
        self.G = {}
        for name, output_array in output_toDict(self.output).items():
            m, u = Aggregator(output_array).getSet(self.samples)
            argmax = u[m==np.max(m)]
            self.G[name] = np.max(argmax)
        return self.G
    
class FirstOfMaximum(Defuzzifier):
    name = "First Of Maximum"
    
    def eval(self):
        self.G = {}
        for name, output_array in output_toDict(self.output).items():
            m, u = Aggregator(output_array).getSet(self.samples)
            argmax = u[m==np.max(m)]
            self.G[name] = np.min(argmax)
        return self.G

    
