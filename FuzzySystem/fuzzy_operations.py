import numpy as np

def algebraic_sum(x, y):
    if not isinstance(x,(list,)):
        x = [x]
    if not isinstance(y,(list,)):
        y = [y]
    if len(x) == len(y):
        return [xi+yi-xi*yi for xi, yi in zip(x,y)]

def algebraic_prod(x,y=None):
    if y is not None:
        if not isinstance(x,(list,)):
            x = [x]
        if not isinstance(y,(list,)):
            y = [y]
        if len(x) == len(y):
            return [xi*yi for xi, yi in zip(x,y)]
    else:
        return np.prod(np.array(x))

def maximum(x,y=None):
    if y is not None:
        if not isinstance(x,(list,)):
            x = [x]
        if not isinstance(y,(list,)):
            y = [y]
        if len(x) == len(y):
            return np.maximum(x,y)
    else:
        return np.max(x)
    
def minimum(x,y=None):
    if y is not None:
        if not isinstance(x,(list,)):
            x = [x]
        if not isinstance(y,(list,)):
            y = [y]
        if len(x) == len(y):
            return np.minimum(x,y)
    else:
        np.min(np.array(x))
    
def union(x,y,type='max'):
    if type=='max':
        return np.squeeze(maximum(x,y))
    elif type=='sum':
        return np.squeeze(algebraic_sum(x,y))
    else:
        raise Exception("Union only by 'max' or 'sum'")

def intersection(x,y,type='min'):
    if type=='min':
        return np.squeeze(minimum(x,y))
    elif type=='prod':
        return np.squeeze(algebraic_prod(x,y))
    else:
        raise Exception("Intersection only by 'min' or 'prod'")
