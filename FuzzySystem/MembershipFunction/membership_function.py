import copy 
import numpy as np
import matplotlib.pyplot as plt
import itertools
import logging, sys
from .. import config
#logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def divide(x,y):
    if y==0:
        return float('inf')
    else:
        return x/y


class MembershipFunction:
    name = 'Membership Function'
    def __init__(self, params, name=None, universe=None):
        self.params=params
        if name is not None:
            self.name = name
        if universe is not None:
            self.universe = universe
        else:
            self.universe=[self.params[0], self.params[-1]]
    
    def eval(self, x):
        pass
    
    @property
    def area(self):
        pass
    
    @property
    def centroid(self):
        pass
    
    def show(self, points=config.default_points):
        #interval = (self.universe[1] - self.universe[0])/100.0
        #u = np.arange(self.universe[0], self.universe[1], interval)
        u = np.linspace(self.universe[0], self.universe[1], num=points, endpoint=True, retstep=False, dtype=None)
        c = [self.eval(e) for e in u]

        fig, ax = plt.subplots()
        ax.plot(u, c, 'r-', label=self.name)
        legend = ax.legend(loc='upper left', shadow=True, fontsize='x-large')
        
        legend.get_frame().set_facecolor('#FFFFFF')
        ax.grid()
        plt.show()
    
    def __str__(self):
        return "class: {0} params: {1}".format(self.__class__.__name__, self.params)


class Trimf(MembershipFunction):
    name = 'Triangular mf'
    
    def eval(self, x):
        self.a = self.params[0]
        self.b = self.params[1]
        self.c = self.params[2]
        return max(min((x-self.a)/(self.b-self.a), (self.c-x)/(self.c-self.b)),0)
    
    def area(self):
        return (self.c-self.a)/2.0
    
    def centroid(self):
        return (self.a+self.b+self.c)/3.0
    

class Gaussmf(MembershipFunction):
    name = 'Gaussian mf'
    
    def eval(self, x):
        self.sigma = self.params[0] 
        self.c = self.params[1]
        return np.exp(-1*(x - self.c)**2/(2.0*self.sigma**2))
    
    def area(self):
        return self.sigma*np.sqrt(2.0*np.pi)

    def centroid(self):
        return self.c


class Logmf(MembershipFunction):
    name = 'Logistic mf'
    
    def eval(self, x):
        a = self.params[0] 
        c = self.params[1]
        #return 1./(1+np.exp(-x))
        return 2./(1+np.exp(((x-c)/a)**2))


class Tanhmf(MembershipFunction):
    name = 'Tanh mf'
    
    def eval(self, x):
        a = self.params[0] 
        c = self.params[1]
        y = 1+np.tanh(-1*((x-c)/a)**2)
        return y


class Sigmoidmf(MembershipFunction):
    name = 'Sigmoid mf'
    
    def eval(self, x):
        a = self.params[0] 
        c = self.params[1]
        y = 1./(1 + np.exp(-a*(x-c)))
        return y


class Cauchymf(MembershipFunction):
    name = 'Cauchy mf'
    
    def eval(self, x):
        a = self.params[0] 
        c = self.params[1]
        y = 1./(1+((x-c)/a)**2)
        return y


class Trapmf(MembershipFunction):
    name = 'Trapezoidal mf'
    
    def eval(self, x):
        self.a = self.params[0]
        self.b = self.params[1]
        self.c = self.params[2]
        self.d = self.params[3]
        return max(min(divide((x-self.a),float(self.b-self.a)), 1, divide((self.d-x),float(self.d-self.c))), 0)
    
    def area(self):
        return (self.d-self.a+self.c-self.b)/2.0
    
    def centroid(self):
        return (self.d**2+self.c*self.d+self.c**2-self.a**2-self.a*self.b-self.b**2)/(3*((self.d-self.a+self.c-self.b)))


class GBellmf(MembershipFunction):
    name = 'Generalized Bell mf'

    def eval(self, x):
        self.a = self.params[0]
        self.b = self.params[1]
        self.c = self.params[2]
        tmp = ((x - self.c)/self.a)**2
        if tmp == 0 and self.b == 0:
            y = 0.5
        elif tmp == 0 and self.b < 0:
            y = 0
        else:
            tmp = tmp**self.b
            y = 1./(1 + tmp)
        return y
