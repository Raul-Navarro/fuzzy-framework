class NonSingleton():
    def __init__(self, mf = None, values=None):
        self.mf = mf
        self.values = values
    
    def eval(self):
        return [self.mf.eval(i) for i in self.values]
    
    def __str__(self):
        return "Non-singleton {}  Range [{} - {}]  Values {}".format(self.mf, min(self.values), 
                max(self.values), len(self.values))
