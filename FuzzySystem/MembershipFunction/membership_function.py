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
    def __init__(self, params, universe=None, name=None, complement=False):
        self.__complement=complement
        self.params=params
        if name is not None:
            self.name = name
        if universe is not None:
            self.universe = universe
        elif self.params is not None:
            self.universe=[self.params[0], self.params[-1]]
        else:
            self.universe=[-10, 10]
    
    def eval(self, x):
        if self.__complement:
            return 1-self.compute(x)
        else:
            return self.compute(x)
    
    def compute(self, x):
        pass
    
    def complement(self):
        self.__complement = not self.__complement
        return self
    
    @property
    def area(self):
        pass
    
    @property
    def centroid(self):
        pass
    
    @property
    def spread(self):
        pass
    
    def set_params(self, params):
        pass
    
    def show(self, points=config.default_points, axes=None, fmt='-', kwargs={}):
        u = np.linspace(self.universe[0], self.universe[1], num=points, endpoint=True, retstep=False, dtype=None)
        #u = np.sort(np.concatenate([u, self.params], axis=0))
        #u = np.unique(u)
        c = [self.eval(e) for e in u]
        if not axes:
            fig, ax = plt.subplots()
        else:
            ax = axes
        ax.plot(u, c, fmt, label=self.name, **kwargs)
        ax.legend(loc='best', fontsize='x-large', fancybox=True, framealpha=0.5)
        #legend.get_frame().set_facecolor('#FFFFFF')
        ax.grid()
        if self.__complement:
            plt.title("complement of {}".format(self.name))
        else:
            plt.title(self.name)
        if not axes:
            plt.show()
    
    def __str__(self):
        return "class: {0} params: {1}".format(self.__class__.__name__, self.params)


class Trimf(MembershipFunction):
    name = 'Triangular mf'

    def __init__(self, params, universe=None, name=None, complement=False):
        self.set_params(params)
        super().__init__(params, universe, name, complement)
    
    def compute(self, x):
        return np.maximum(np.minimum((x-self.a)/(self.b-self.a), (self.c-x)/(self.c-self.b)),0)
    
    def area(self):
        return (self.c-self.a)/2.0
    
    def centroid(self):
        return (self.a+self.b+self.c)/3.0
    
    @property
    def spread(self):
        return self.c - self.a
    
    def set_params(self, params):
        self.a = params[0]
        self.b = params[1]
        self.c = params[2]

class Gaussmf(MembershipFunction):
    name = 'Gaussian mf'
    
    def __init__(self, params, universe=None, name=None, complement=False):
        self.set_params(params)
        super().__init__(params, universe, name, complement)
        
    
    def compute(self, x):
        return np.exp(-1*(x - self.c)**2/(2.0*self.sigma**2))
    
    def area(self):
        return self.sigma*np.sqrt(2.0*np.pi)

    def centroid(self):
        return self.c
    
    @property
    def spread(self):
        return self.sigma
    
    def set_params(self, params):
        self.sigma = params[0] 
        self.c = params[1]



class Logmf(MembershipFunction):
    name = 'Logistic mf'
    
    def __init__(self, params, universe=None, name=None, complement=False):
        self.set_params(params)
        super().__init__(params, universe, name, complement)
    
    def compute(self, x):
        #return 1./(1+np.exp(-x))
        return 2./(1+np.exp(((x-self.c)/self.a)**2))
    
    @property
    def spread(self):
        return self.a
    
    def set_params(self, params):
        self.a = params[0] 
        self.c = params[1]
    

class Tanhmf(MembershipFunction):
    name = 'Tanh mf'
    
    def __init__(self, params, universe=None, name=None, complement=False):
        self.set_params(params)
        super().__init__(params, universe, name, complement)
    
    def compute(self, x):
        y = 1+np.tanh(-1*((x-self.c)/self.a)**2)
        return y
    
    @property
    def spread(self):
        return self.a
    
    def set_params(self, params):
        self.a = params[0] 
        self.c = params[1]


class Sigmoidmf(MembershipFunction):
    name = 'Sigmoid mf'
    
    def __init__(self, params, universe=None, name=None, complement=False):
        self.set_params(params)
        super().__init__(params, universe, name, complement)
    
    def compute(self, x):
        y = 1./(1 + np.exp(-self.a*(x-self.c)))
        return y
    
    @property
    def spread(self):
        return self.a
    
    def set_params(self, params):
        self.a = params[0] 
        self.c = params[1]


class Cauchymf(MembershipFunction):
    name = 'Cauchy mf'
    
    def __init__(self, params, universe=None, name=None, complement=False):
        self.set_params(params)
        super().__init__(params, universe, name, complement)
    
    def compute(self, x):
        y = 1./(1+((x-self.c)/self.a)**2)
        return y
    
    @property
    def spread(self):
        return self.a
    
    def set_params(self, params):
        self.a = params[0] 
        self.c = params[1]

class Trapmf(MembershipFunction):
    name = 'Trapezoidal mf'
    
    def __init__(self, params, universe=None, name=None, complement=False):
        self.set_params(params)
        super().__init__(params, universe, name, complement)
    
    def compute(self, x):
        if isinstance(x, (list,np.ndarray,)):
            return np.array([max(min(divide((xi-self.a),float(self.b-self.a)), 1, divide((self.d-xi),float(self.d-self.c))), 0) for xi in x])
        else:
            return max(min(divide((x-self.a),float(self.b-self.a)), 1, divide((self.d-x),float(self.d-self.c))), 0)

    @property
    def spread(self):
        return self.d-self.a
    
    def area(self):
        return (self.d-self.a+self.c-self.b)/2.0
    
    def centroid(self):
        return (self.d**2+self.c*self.d+self.c**2-self.a**2-self.a*self.b-self.b**2)/(3*((self.d-self.a+self.c-self.b)))
    
    def set_params(self, params):
        self.a = params[0]
        self.b = params[1]
        self.c = params[2]
        self.d = params[3]


class GBellmf(MembershipFunction):
    name = 'Generalized Bell mf'
    
    def __init__(self, params, universe=None, name=None, complement=False):
        self.set_params(params)
        super().__init__(params, universe, name, complement)

    def compute(self, x):
        tmp = ((x - self.c)/self.a)**2
        if tmp == 0 and self.b == 0:
            y = 0.5
        elif tmp == 0 and self.b < 0:
            y = 0
        else:
            tmp = tmp**self.b
            y = 1./(1 + tmp)
        return y
        
    @property
    def spread(self):
        return self.a
    
    def set_params(self, params):
        self.a = params[0]
        self.b = params[1]
        self.c = params[2]
