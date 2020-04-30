import copy
import numpy as np
import matplotlib.pyplot as plt
import itertools
import logging, sys

from .matlab_importer import import_fis_matlab

#logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

from .FuzzySet.fuzzyset import FuzzySet
from .FuzzyVariable.fuzzyvariable import FuzzyVariable
from .Defuzzifier.defuzzifier import *
from .FuzzyInferenceSystem.fis import FuzzyInferenceSystem
from .FuzzyInferenceSystem.fuzzyrule import Antecedent, Consequent, FuzzyRule, TSKConsequent
from .FuzzyInferenceSystem.output import Output
from .MembershipFunction import Trimf, Gaussmf, Trapmf, Sigmoidmf, GBellmf, Logmf, Cauchymf, Tanhmf
from .NonSingleton import NonSingleton