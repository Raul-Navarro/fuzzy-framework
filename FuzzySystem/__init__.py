import copy 
import numpy as np
import matplotlib.pyplot as plt
import itertools
import logging, sys

#logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)



from . import MembershipFunction as mf, FuzzySet, FuzzyVariable, FuzzyInferenceSystem, Defuzzifier
from .FuzzyInferenceSystem.fuzzyrule import Antecedent, Consequent, FuzzyRule
#from MembershipFunction import from .membership_function import Trimf, Gaussmf, Trapmf, Sigmoidmf, GBellmf, Logmf, Cauchymf, Tanhmf
