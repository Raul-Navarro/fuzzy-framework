# Copyright (c) 2020 Raul Navarro-Almanza,
#   Universidad Autónoma de Baja California
#
# SPDX-License-Identifier: MIT
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


class NonSingleton():
    def __init__(self, mf=None, values=None):
        self.mf = mf
        self.values = values

    def eval(self):
        return [self.mf.eval(i) for i in self.values]

    def __str__(self):
        return "\n Non-singleton {}  \n  Range: [{} - {}]  \n  Values: {}".format(
            self.mf, min(self.values), max(self.values), len(self.values))
