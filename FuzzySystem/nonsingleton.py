# Copyright (c) 2020 Raul Navarro-Almanza,
#   Universidad Autónoma de Baja California
#
# SPDX-License-Identifier: MIT
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


class NonSingleton:
    '''A Class for representing Non-singleton inputs to the system

    :param mf: Membership Function to map the input
    :type mf: MembershipFunction
    :param values: Actual crisp numbers to evaluate the input
    '''

    def __init__(self, mf=None, values=None):
        self.mf = mf
        self.values = values

    def eval(self):
        '''Performs the Non-singleton evaluation

        :return: Resulted values from the function evaluation characterized by a MembershipFunction object
        '''
        return self.mf.eval(self.values)

    def __str__(self):
        return "\n Non-singleton {}  \n  Range: [{} - {}]  \n  Values: {}".format(
            self.mf, min(self.values), max(self.values), len(self.values))
