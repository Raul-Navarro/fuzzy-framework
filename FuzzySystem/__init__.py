"""A python framework to build Fuzzy Inference Systems

    Raul Navarro-Almanza <rnavarro@uabc.edu.mx>
"""

from FuzzySystem.defuzzifier import *
from FuzzySystem.membership_function import *
from FuzzySystem.nonsingleton import *
from FuzzySystem.fis import FuzzyInferenceSystem
from FuzzySystem.fuzzyrule import Antecedent, Consequent, FuzzyRule, TSKConsequent
from FuzzySystem.output import Output
from FuzzySystem.fuzzyset import FuzzySet
from FuzzySystem.fuzzyvariable import FuzzyVariable
from .matlab_importer import import_fis_matlab
from .utils import fuzzy_similarity
