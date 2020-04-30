import pandas as pd
import numpy as np
from .fuzzy_operations import minimum, maximum, algebraic_prod, algebraic_sum


def format_inputs(x, inputs=None, data_columns=None, verbose=False):
    if isinstance(x, (np.ndarray, )):
        if data_columns is not None:
            x = dict(zip(data_columns, x.T))
        else:
            if input is not None:
                x = dict(zip(list(inputs.keys()), x.T))
            raise Exception('Inputs dictionary or list must be provided')

    elif isinstance(x, (pd.DataFrame, )):
        x = x.to_dict(orient='list')

    elif isinstance(x, (tuple, )):
        x = dict(x)

    if isinstance(x, (dict, )):
        if verbose:
            print('Inputs:')
            for k in x.keys():
                print('{}: {}'.format(k, x[k]))
        return x
    raise Exception('Input must be a dictionary or an array')


def get_fuzzy_operators(and_op, or_op):
    if isinstance(and_op, (str, )):
        if and_op == 'min':
            and_op = minimum
        elif and_op == 'prod':
            and_op = algebraic_prod
        else:
            raise Exception(
                "Choose the correct operator either 'prod' or 'min'")
    if isinstance(or_op, (str, )):
        if or_op == 'max':
            or_op = maximum
        elif or_op == 'sum':
            or_op = algebraic_sum
        else:
            raise Exception(
                "Choose the correct operator either 'sum' or 'max'")
    return and_op, or_op
