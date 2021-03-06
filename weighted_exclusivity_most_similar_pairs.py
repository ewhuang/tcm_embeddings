#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

from collections import OrderedDict
import datetime
from create_med2vec_input import get_patient_dct
import os
import subprocess
import sys
import time

date_format = '%Y-%m-%d'

def generate_directories():
    results_dir = './results/wext/'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

def read_code_list():
    code_list = []
    f = open('./results/code_list.txt', 'r')
    for line in f:
        code_list += [line.strip()]
    f.close()
    return code_list

def write_mutation_file(patient_dct, fname, code_list):
    '''
    Given the patient dictioary, write out the file in mutation format. First
    column is the sample name, every other column is the name of a symptom or
    herb.
    '''
    patient_num = 0
    out = open(fname, 'w')
    for key in patient_dct:
        visit_dct = patient_dct[key]
        # Skip patients that only had one visit.
        if len(visit_dct) == 1:
            continue
        visit_num = 0
        for date in sorted(visit_dct.keys()):
            disease_list, symptom_list, herb_list = visit_dct[date]
            symptom_list = [code_list.index(symp) for symp in symptom_list]
            herb_list = [code_list.index(herb) for herb in herb_list]
            out.write('p%d%d\t%s\t%s\n' % (patient_num, visit_num,
                '\t'.join(map(str, symptom_list)), '\t'.join(map(str,
                    herb_list))))
            visit_num += 1
        patient_num += 1
    out.close()

def call_process_mutations(mut_fname, wext_out_fname):
    '''
    Calls WExt's process_mutations.py script.
    '''
    command = ('python ./wext/process_mutations.py -ct "tcm" -m %s -o %s' % (
        mut_fname, wext_out_fname))
    subprocess.call(command, shell=True)

def call_compute_mut_probs(wext_out_fname, prob_out_fname):
    '''
    Calls WExt's compute_mutation_probabilities.py script.
    '''
    command = ('python ./wext/compute_mutation_probabilities.py -np 5000 -m '
        '%s -wf %s -nc 5' % (wext_out_fname, prob_out_fname))
    subprocess.call(command, shell=True)

def call_find_exclusive_sets(wext_out_fname, ex_set_out_fname, set_size):
    '''
    Calls WExt's find_exclusive_sets.py script.
    '''
    command = ('python ./wext/find_exclusive_sets.py -mf %s -o %s -f 5 -c 5 '
        '-ks %s -N 1000 RE -m Exact' % (wext_out_fname, ex_set_out_fname,
            set_size))
    print command
    subprocess.call(command, shell=True)

def read_code_file(code_type):
    '''
    Given a code type, read the file to get the list of unique codes within
    that type.
    '''
    data = {}
    f = open('./data/%s_count_dct.txt' % code_type, 'r')
    for line in f:
        line = line.split()
        data[line[0]] = int(line[1])
    f.close()
    return data

def translate_int_to_chinese(code_list, ex_set_out_fname, set_size):
    '''
    Takes the output of WExt, and translates the integer codes back to Chinese.
    Only outputs groups of codes that contain at least one herb and one symptom.
    '''
    herb_count_dct = read_code_file('herb')
    f = open(ex_set_out_fname + '-sampled-sets.tsv', 'r')
    out = open(ex_set_out_fname + '-sampled-sets-chinese.tsv', 'w')
    for i, line in enumerate(f):
        if i == 0:
            out.write(line)
            continue
        candidate_codes = [0 for i in range(set_size)]
        line = line.strip().split('\t')
        candidate_codes = [code_list[int(code)] for code in line[0].split(',')]
        # TODO: Currently skipping dosages. Find a deeper way to remove these.
        if True in ['G' in code for code in candidate_codes]:
            continue
        # Skip a co-occurrence if all three items are symptoms, or if all three
        # are herbs.
        cand_are_herbs = [code in herb_count_dct for code in candidate_codes]
        if False not in cand_are_herbs or True not in cand_are_herbs:
            continue
        out.write('%s\t%s\n' % (','.join(candidate_codes), '\t'.join(line[1:])))
    out.close()
    f.close()

def main():
    if len(sys.argv) != 2:
        print 'Usage: python %s 2/3' % (sys.argv[0])
        exit()
    set_size = int(sys.argv[1])
    generate_directories()
    code_list = read_code_list()
    patient_dct = get_patient_dct()

    # Create mutation file.
    mut_fname = './data/wext_mutation_file.txt'
    write_mutation_file(patient_dct, mut_fname, code_list)

    # Process mutation file.
    wext_out_fname = './results/wext/mutation_file_output.txt'
    call_process_mutations(mut_fname, wext_out_fname)

    # Compute mutation probabilities.
    prob_out_fname = './results/wext/weight_file_output'
    call_compute_mut_probs(wext_out_fname, prob_out_fname)

    ex_set_out_fname = './results/wext/%d_set_output' % set_size
    call_find_exclusive_sets(wext_out_fname, ex_set_out_fname, set_size)

    translate_int_to_chinese(code_list, ex_set_out_fname, set_size)

if __name__ == '__main__':
    start_time = time.time()
    main()
    print "---%f seconds---" % (time.time() - start_time)