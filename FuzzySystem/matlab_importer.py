# Copyright (c) 2020 Raul Navarro-Almanza,
#   Universidad Autónoma de Baja California
#
# SPDX-License-Identifier: MIT
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from FuzzySystem.fis import FuzzyInferenceSystem
from FuzzySystem.fuzzyrule import FuzzyRule, Antecedent, Consequent
from FuzzySystem.fuzzyset import FuzzySet
from FuzzySystem.fuzzyvariable import FuzzyVariable
from FuzzySystem.membership_function import Trapmf, Trimf, Gaussmf, GBellmf, Sigmoidmf

"""
Membership functions in matlab: 
dsigmf, evalmf, gauss2mf, gaussmf,
gbellmf, mf2mf, pimf, psigmf, 
sigmf, smf, trapmf, trapmf, trimf, zmf
"""

MF_DICTIONARY = {
    'trapmf': Trapmf,
    'trimf': Trimf,
    'gaussmf': Gaussmf,
    'gbellmf': GBellmf,
    'sigmf': Sigmoidmf
}


def strip_array(array):
    ''':meta private:'''
    return [text.strip() for text in array if text.strip() != '']


def read_rules_matlab(file=None, txt=None):
    ''':meta private:'''
    rules_array = []
    if file is not None:
        with open(file, 'r') as f:
            for text in f:
                rules, conection = text.split(':')
                ant, con = rules.split(',')
                ants = strip_array(ant.split(' '))
                cons = strip_array(con.split(' '))
                weights = cons[-1].strip().replace('(', '').replace(')', '')
                cons = cons[:-1]
                conection = conection.strip()
                rules_array.append((ants, cons, weights, conection))
    elif txt is not None:
        for text in txt:
            rules, conection = text.split(':')
            ant, con = rules.split(',')
            ants = strip_array(ant.split(' '))
            cons = strip_array(con.split(' '))
            weights = cons[-1].strip().replace('(', '').replace(')', '')
            cons = cons[:-1]
            conection = conection.strip()
            rules_array.append((ants, cons, weights, conection))
    else:
        return None
    return rules_array


def import_rules_matlab(rules, fis_inputs, fis_outputs):
    ''':meta private:'''
    antecedent = []
    consequent = []
    fis_rules = None
    for i, rule in enumerate(rules):
        antecedent.append(Antecedent(conector='min'))
        consequent.append(Consequent())

        for j, a in enumerate(rule[0]):
            antecedent[i].add(fis_inputs[j][int(a) - 1])
        for j, c in enumerate(rule[1]):
            consequent[i].add(fis_outputs[j][int(c) - 1])

        fis_rules = []
        for i in range(len(antecedent)):
            fis_rules.append(
                FuzzyRule(antecedent=antecedent[i], consequent=consequent[i]))
    return fis_rules


def read_fis_file(file):
    ''':meta private:'''
    fis_config = {}
    i = 1
    sections = ['[System]', '[Input{}]', '[Output{}]', '[Rules]']
    with open(file, 'r') as f:
        line = f.readline()
        if line.strip() == sections[0]:
            fis_config['system'] = {}
            text = f.readline()
            while text.strip() != '':
                key, value = text.split("=")
                fis_config['system'][key] = value.strip().replace("'", '')
                text = f.readline()
        fis_config['system']['NumInputs'] = int(
            fis_config['system']['NumInputs'])
        inputs = fis_config['system']['NumInputs']
        fis_config['system']['NumOutputs'] = int(
            fis_config['system']['NumOutputs'])
        outputs = int(fis_config['system']['NumOutputs'])
        fis_config['inputs'] = []
        while i <= inputs:
            text = f.readline()
            while text.strip() != '':
                if text.strip() == sections[1].format(i):
                    temp = {}
                else:
                    key, value = text.strip().split('=')
                    if key == 'Range':
                        value = value.replace('[', '').replace(']', '')
                        #value = list(map(int,value.split(' ')))
                        value = list(map(float, value.split(' ')))
                        temp[key] = value
                    elif key == 'NumMFs':
                        temp[key] = int(value)
                    else:
                        temp[key] = value.strip().replace("'", '')
                text = f.readline()
            i = i + 1
            fis_config['inputs'].append(temp)
        i = 1
        fis_config['outputs'] = []
        while i <= outputs:
            text = f.readline()
            while text.strip() != '':
                if text.strip() == sections[2].format(i):
                    temp = {}
                else:
                    key, value = text.strip().split('=')
                    if key == 'Range':
                        value = value.replace('[', '').replace(']', '')
                        value = list(map(int, value.split(' ')))
                        temp[key] = value
                    elif key == 'NumMFs':
                        temp[key] = int(value)
                    else:
                        temp[key] = value.strip().replace("'", '')
                text = f.readline()
            i = i + 1
            fis_config['outputs'].append(temp)
        text = f.readline()
        if text.strip() == sections[3]:
            text = f.read()
            fis_config['rules'] = text.strip().split('\n')
    return fis_config


def parse_fis_file(conf):
    ''':meta private:'''
    for inp in range(0, int(conf['system']['NumInputs'])):
        num_mf = int(conf['inputs'][inp]['NumMFs'])
        fuzzy_sets = []
        for i in range(1, num_mf + 1):
            name_mf, params = conf['inputs'][inp]['MF' + str(i)].split(',')
            name, mf = name_mf.split(':')
            params = params.replace('[', '').replace(']', '')
            params = list(map(float, params.split(' ')))
            fuzzy_sets.append((name, mf, params))
            del conf['inputs'][inp]['MF' + str(i)]
        conf['inputs'][inp]['values'] = fuzzy_sets

    for inp in range(0, int(conf['system']['NumOutputs'])):
        num_mf = int(conf['outputs'][inp]['NumMFs'])
        fuzzy_sets = []
        for i in range(1, num_mf + 1):
            name_mf, params = conf['outputs'][inp]['MF' + str(i)].split(',')
            name, mf = name_mf.split(':')
            params = params.replace('[', '').replace(']', '')
            params = list(map(float, params.split(' ')))
            fuzzy_sets.append((name, mf, params))
            del conf['outputs'][inp]['MF' + str(i)]
        conf['outputs'][inp]['values'] = fuzzy_sets
    return conf


def get_io_fis(conf):
    ''':meta private:'''
    fis_input = []
    for input in conf['inputs']:
        fuzzy_sets = []
        for fs in input['values']:
            fuzzy_sets.append(FuzzySet(fs[0], MF_DICTIONARY[fs[1]](fs[2])))
        fis_input.append(
            FuzzyVariable(input['Name'], fuzzy_sets, universe=input['Range']))

    fis_output = []
    for output in conf['outputs']:
        fuzzy_sets = []
        for fs in output['values']:
            fuzzy_sets.append(FuzzySet(fs[0], MF_DICTIONARY[fs[1]](fs[2])))
        fis_output.append(
            FuzzyVariable(output['Name'], fuzzy_sets,
                          universe=output['Range']))
    return (fis_input, fis_output)


def import_fis_matlab(file):
    '''Function to import a matlab type fis file to create an FuzzySystem object

    :param file: [str] path to the file to import
    :return: [FuzzySystem] a FuzzySystem equivalent to the input fis configuration file
    '''
    conf = read_fis_file(file)
    conf = parse_fis_file(conf)
    fis_input, fis_output = get_io_fis(conf)
    rules = read_rules_matlab(txt=conf['rules'])
    fis_rules = import_rules_matlab(rules, fis_input, fis_output)
    fis = FuzzyInferenceSystem(fis_rules, inputs=fis_input, outputs=fis_output)
    return fis
