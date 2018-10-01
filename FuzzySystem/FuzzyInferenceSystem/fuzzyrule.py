import copy

class Conector:
    def __init__(self, operator, inputs = None):
        self.operator = operator
        if inputs is not None:
            self.inputs = inputs
    
    def eval(self, param1, param2):
        return self.operator(param1, param2)
    
    def __call__(self, param1, param2, conector=min):
        if isinstance(param1, Agregation):
            return self(self(param1.prop1, param1.prop2, param1.conector), param2, conector)
        if isinstance(param2, Agregation):
            return self(self(param2.prop1, param2.prop2, param2.conector), param1, conector)
        if isinstance(param1, Proposition):
            #print(param1.fuzzyvar.name, param1.fuzzyset, self.inputs[param1.fuzzyvar.name])
            param1 = param1.fuzzyvar.get(param1.fuzzyset).eval(self.inputs[param1.fuzzyvar.name])
        if isinstance(param2, Proposition):
            #print(param2.fuzzyvar.name, param2.fuzzyset,self.inputs[param2.fuzzyvar.name])
            param2 = param2.fuzzyvar.get(param2.fuzzyset).eval(self.inputs[param2.fuzzyvar.name])
        #logging.debug("Debug: ",param1, conector, param2, '=', conector(param1, param2))
        return conector(param1, param2)

class Proposition:
    def __init__(self, fuzzyvar, fuzzyset):
        self.fuzzyvar = fuzzyvar
        self.fuzzyset = fuzzyset
        
    def __getitem__(self, index):
        if index is 0:
            return self.fuzzyvar
        elif index is 1: 
            return self.fuzzyset
        else:
            return None
        
    def __and__(self, other):
        #print('Debug: ', self, 'AND', other)
        return Agregation(self, other, min)
    
    def __or__(self, other):
        #print('Debug: ', self, 'OR', other)
        return Agregation(self, other, max)
    
    def add(self, other, conector):
        return Agregation(self, other, conector)
    
    def getfuzzyset(self):
        result = self.fuzzyvar.get(self.fuzzyset)
        if result is not None:
            return copy.copy(result)
        
    def __str__(self):
        return "{} is {}".format(self.fuzzyvar.name, self.fuzzyset)
    
class Agregation:
    def __init__(self, prop1, prop2, conector):
        self.prop1 = prop1
        self.prop2 = prop2
        self.conector = conector
        self.parent = None
        
    def __and__(self, other):
        #print(self, other)
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
    
    def eval(self,x):
        #logging.debug("Debug: ", "Agregation inputs:", dict(x) )
        op = Conector(self.conector, dict(x))
        return op(self.prop1, self.prop2, self.conector)
    
    def __str__(self):
        return 'TODO'

class Antecedent:
    def __init__(self, proposition=None, conector = None):
        self.conector = conector
        if proposition is None:
            self.propositions = []
        else:
            if isinstance(proposition, (list, Agregation, )):
                #logging.debug("Debug: Constructor: preposition is Agregation")
                self.propositions = proposition
            else:
                self.propositions = [proposition]
    
    def get(self, variable):
        for prop in self.propositions:
            ##print('Debug: ', prop[0].name)
            if(variable == prop[0].name):
                return prop[0].get(prop[1])
        #print("Variable {} does not exist".format(variable))
        return None
        
    def add(self, other):
        self.propositions.append(other)
        
    def eval(self, x):
        if isinstance(self.propositions, (Agregation,)):
            #logging.debug("Debug: Evaluation: preposition is Agregation")
            return self.propositions.eval(x)
        
        if isinstance(x, (dict,)):
            #x = list(x)
            x = list(zip(x.keys(), x.values()))
            
        if isinstance(x, (list,)):
            result = []
#             for variable, value in x:
#                 fvar = self.get(variable)
#                 if fvar:
#                     result.append(fvar.eval(value))
            result = [self.get(variable).eval(value) for variable, value in x if self.get(variable) ]
            if self.conector is not None:
                return self.conector(result)
            return result    
        else:
            return self.get(x[0]).eval(x[1])
        
    def show(self):
        print(self)
        
    def __str__(self):
        if isinstance(self.propositions, (list,)):
            #return ' and '.join(["{} is {}".format(var.name, value) for var, value in self.propositions])
            return ' and '.join(["{}".format(str(prop)) for prop in self.propositions])
        if isinstance(self.propositions, (Agregation,)):
           return str(self.propositions)
        return 'EMPTY'
        

class Consequent:
    def __init__(self, proposition=None, conector = None):
        self.conector = conector
        if proposition is None:
            self.propositions = []
        else:
            if isinstance(proposition, (list,)):
                self.propositions = proposition
            else:
                self.propositions = [proposition]
    
    def get(self, variable):
        for prop in self.propositions:
            if(variable == prop[0].name):
                return prop[0].get(prop[1])
        return None
        
    def add(self, other):
        self.propositions.append(other)
        
    def eval(self, x):
        result = []
        if isinstance(x, (float,int,)):
            for prop in self.propositions:
                #print('DEBUG Consequent propositions',prop)
                result.append((prop.fuzzyvar.name, prop.getfuzzyset().cut(x)))
            return result
            
#         if isinstance(x, (dict,)):
#             x = list(zip(x.keys(), x.values()))
            
        if isinstance(x, (list,)):
            for prop in self.propositions:
                result.append((prop.fuzzyvar.name, prop.getfuzzyset().cut(x[0])))
            return result
#             #logging.debug("Debug: ", "Consequent: ", "eval number: ", x)
#             result = [self.get(variable).eval(value) for variable, value in x if self.get(variable)]
#             if self.conector:
#                 return self.conector(result)
#             return result    
#         if isinstance(tuple,):
#             return self.get(x[0]).eval(x[1])
        
    def __str__(self):
        if isinstance(self.propositions, (list)):
            output = []
            for prop in self.propositions:
                if isinstance(prop, (tuple,)):
                    output.append(" {} is {} ".format(prop[0].name, prop[1]))
                elif isinstance(prop, (Proposition,)):
                    output.append(str(prop))
            if len(output)>1:
                return ' and '.join(output)
            else:
                return output[0]
    def show(self):
        print(self)



class FuzzyRule():
    def __init__(self, antecedent=None, consequent=None, conector=None):
        self.antecedent = antecedent
        
        if isinstance(consequent, (list,Consequent,)):
            self.consequent = consequent
        else:
            #Proposition class
            self.consequent = [consequent]
        self.conector = conector
        
    def eval(self, x):
        #print("\nDEBUG: Fuzzy Rule Evaluation")
        firing_strength = self.antecedent.eval(x)
        print('\t{} = {}'.format(str(self), firing_strength))
        #logging.debug("Debug: Firing Strength: ", firing_strength)
        if isinstance(self.consequent, (Consequent,)):
            return self.consequent.eval(firing_strength)
        return [prop.eval(firing_strength) for prop in self.consequent]
    
    def __str__(self):
        if isinstance(self.consequent, (Consequent,)):
            return "IF {} THEN {}".format(str(self.antecedent), 
                                      ' and '.join([str(cons) for cons in self.consequent.propositions]))
        if isinstance(self.consequent, (list,)):
            return "IF {} THEN {}".format(str(self.antecedent), 
                                      ' and '.join([str(cons) for cons in self.consequent]))
        
    def show(self):
        print(self)
