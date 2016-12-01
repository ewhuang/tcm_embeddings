### Author: Edward Huang

import cPickle

# This script creates the visit binary matrix. Must run create_med2vec_input.py
# first.

def read_code_list():
    '''
    Reads the list of symptoms and herbs.
    '''
    code_list = []
    f = open('./results/code_list.txt', 'r')
    for line in f:
        code_list += [line.strip()]
    f.close()
    return code_list

def convert_to_binary_matrix(patient_matrix, code_list):
    '''
    Returns a 2D list containing the visits and entries of each patient.
    '''
    binary_matrix = []
    for patient_matrix_row in patient_matrix:
        if patient_matrix_row == [-1]:
            continue
        binary_matrix_row = [0 for i in range(len(code_list))]
        for code_int in patient_matrix_row:
            binary_matrix_row[code_int] = 1
        binary_matrix += [binary_matrix_row]
    return binary_matrix

def main():
    code_list = read_code_list()
    f = open('./results/med2vec_input_baseline.pickle', 'r')
    patient_matrix = cPickle.load(f)
    f.close()
    binary_matrix = convert_to_binary_matrix(patient_matrix, code_list)
    out = open('./data/visit_binary_matrix.txt', 'w')
    for line in binary_matrix:
        out.write(','.join(map(str, line)) + '\n')
    out.close()

if __name__ == '__main__':
    main()