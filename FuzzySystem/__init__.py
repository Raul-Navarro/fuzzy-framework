import copy 
import numpy as np
import matplotlib.pyplot as plt
import itertools
import logging, sys

from .matlab_importer import import_fis_matlab


#logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)



#from .MembershipFunction.membership_function import MembershipFunction
#from. FuzzySet.fuzzyset import FuzzySet
#from .FuzzyVariable.fuzzyvariable import FuzzyVariable
#from .Defuzzifier.defuzzifier import Defuzzifier
#from .FuzzyInferenceSystem.fis import FuzzyInferenceSystem
#from .FuzzyInferenceSystem.fuzzyrule import Antecedent, Consequent, FuzzyRule
#from .FuzzyInferenceSystem.output import Output
#from MembershipFunction import from .membership_function import Trimf, Gaussmf, Trapmf, Sigmoidmf, GBellmf, Logmf, Cauchymf, Tanhmf
