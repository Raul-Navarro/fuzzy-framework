class Defuzzifier:
    name = "Defuzzifier"
    def __init__(self, output):
        self.output = output
    
    def eval(self):
        pass

class Centroid(Defuzzifier):
    name = "Centroid"
    def eval(self):
        result = {}
        for key in self.output.get_outputs():
            result[key] = sum(self.output.universe(key, 'list')*self.output.values(key))/sum(self.output.values(key))
        return result
