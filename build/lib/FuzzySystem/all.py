# Copyright (c) 2020 Raul Navarro-Almanza,
#   Universidad Autónoma de Baja California
#
# SPDX-License-Identifier: MIT
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import copy
import numpy as np
import matplotlib.pyplot as plt
import itertools
import logging, sys

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
default_points = 100
#Centroid, Center of sums, Alturas,
