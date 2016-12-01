#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

from datetime import datetime
import numpy as np
import operator
import os
from scipy.linalg import svd
from scipy.spatial.distance import pdist, squareform
import time

date_format = '%Y-%m-%d'

### This script constructs a co-occurrence matrix of symptoms and herbs. Then,
### it performs SVD, and gets the low-dimensional vector for each code. We 
### then find the most similar pairs by cosine similarity.

def get_patient_dct():
    '''
    Returns dictionary
    Key: (name, date of birth) -> (str, str)
    Value: dictionary, where keys are (name, DOB) pairs and values are tuples
    containing the diseases, diagnosis dates, symptoms, and herbs of each visit.
    '''
    patient_dct = {}
    f = open('./data/HIS_tuple_word.txt', 'r')
    for i, line in enumerate(f):
        diseases, name, dob, diagnosis_date, symptoms, herbs = line.split('\t')
        # Always ends with a colon, so the last element of the split will be
        # the empty string.
        disease_list = diseases.split(':')[:-1]
        
        diagnosis_date = diagnosis_date.split('，')[1][:len('xxxx-xx-xx')]
        # Format the diagnosis date.
        diagnosis_date = datetime.strptime(diagnosis_date, date_format)

        symptom_list = symptoms.split(':')[:-1]
        herb_list = herbs.split(':')[:-1]
        # Skip visits that don't have a complete record.
        if len(symptom_list) == 0 or len(herb_list) == 0:
            continue

        # Add the listing to the dictionary.
        key = (name, dob)
        # Each unique patient is its own dictionary.
        if key not in patient_dct:
            patient_dct[key] = {}
        # Remove duplicates from our symptom and herb list.
        patient_dct[key][diagnosis_date] = (disease_list, list(set(symptom_list
            )), list(set(herb_list)))
    f.close()

    return patient_dct

def read_code_list():
    '''
    Fetches the unique codes as run by create_med2vec_input.py.
    '''
    code_list = []
    f = open('./results/code_list.txt', 'r')
    for line in f:
        code_list += [line.strip()]
    f.close()
    return code_list

def read_code_file(code_type):
    '''
    Given a code type, read the file to get the list of unique codes within
    that type.
    '''
    data = {}
    f = open('./data/%s_count_dct.txt' % code_type, 'r')
    for line in f:
        line = line.split()
        data[line[0]] = float(line[1])
    f.close()
    return data

def write_scores_to_file(model_type, similarity_dct):
    '''
    Given a similarity dictionary and a model type, write out the similarity
    scores to file. The scores are either cosine for SVD baseline, or just
    the co-occurrence count for the co-occurrence baseline. Writes out a file
    for each of herb-herb, herb-symptom, and symptom-symptom scores.
    '''

    herb_count_dct = read_code_file('herb')
    symptom_count_dct = read_code_file('symptom')

    # We only want 1000 of herb-herb, symptom-symptom, and herb-symptoms.
    hh_count, ss_count, hs_count = 0, 0, 0

    # Write out to one of three files.
    out_folder = './results/%s_baseline' % model_type
    ss_out = open('%s/ss_pair_similarities.txt' % out_folder, 'w')
    hs_out = open('%s/hs_pair_similarities.txt' % out_folder, 'w')
    hh_out = open('%s/hh_pair_similarities.txt' % out_folder, 'w')
    for (code_a, code_b), score in similarity_dct:
        a_is_herb = code_a in herb_count_dct
        b_is_herb = code_b in herb_count_dct

        # Skip herbs and symptoms that appear in fewer than 10 visits.
        if a_is_herb:
            a_count = herb_count_dct[code_a]
        else:
            a_count = symptom_count_dct[code_a]
        if b_is_herb:
            b_count = herb_count_dct[code_b]
        else:
            b_count = symptom_count_dct[code_b]
        if a_count < 10 or b_count < 10:
            continue

        # Decide which file to write to.
        out_str = '%s\t%s\t%f\t%d\t%d\n' % (code_a, code_b, score, a_count,
            b_count)
        if a_is_herb and b_is_herb:
            if hh_count == 1000:
                continue
            hh_out.write(out_str)
            hh_count += 1
        elif not a_is_herb and not b_is_herb:
            if ss_count == 1000:
                continue
            ss_out.write(out_str)
            ss_count += 1
        else:
            if hs_count == 1000:
                continue
            hs_out.write(out_str)
            hs_count += 1
    
    ss_out.close()
    hs_out.close()
    hh_out.close()

def build_pmi_dct(co_occ_dct):
    '''
    Given the co-occurrence dictionary, simply divide each value by the counts
    of its keys to get the pointwise mutual information.
    '''
    pmi_dct = {}

    code_count_dct = read_code_file('herb')
    code_count_dct.update(read_code_file('symptom'))

    for code_a, code_b in co_occ_dct:
        if co_occ_dct[(code_a, code_b)] == 0:
            continue
        pmi_dct[(code_a, code_b)] = np.log2(co_occ_dct[(code_a, code_b)] /
            (code_count_dct[code_a] * code_count_dct[code_b]))

    pmi_dct = sorted(pmi_dct.items(), key=operator.itemgetter(1), reverse=True)
    write_scores_to_file('pmi', pmi_dct)

def build_cooccurrence_matrix(patient_dct, code_list):
    '''
    If code_list has n elements, build an n x n matrix of co-occurrence values.
    Also writes out the top pairs as scored by co-occurrence counts.
    '''
    # Initialize the matrix.
    co_occ_matrix = [[0.0 for i in range(len(code_list))] for j in range(len(
        code_list))]

    # The dictionary is for co-occurrence baseline purposes. Matrix is for SVD.
    co_occ_dct = {}

    for key in patient_dct:
        visit_dct = patient_dct[key]
        # Skip patients that only had one visit.
        if len(visit_dct) == 1:
            continue

        for date in sorted(visit_dct.keys()):
            disease_list, symptom_list, herb_list = visit_dct[date]

            combined_list = symptom_list + herb_list
            for a in range(len(combined_list)):
                code_a = combined_list[a]
                for b in range(a + 1, len(combined_list)):
                    code_b = combined_list[b]
                    # Update the dictionary in addition to the matrix.
                    if (code_a, code_b) not in co_occ_dct:
                        co_occ_dct[(code_a, code_b)] = 0.0
                    co_occ_dct[(code_a, code_b)] += 1

            # Convert each symptom/herb to their index in the code list.
            visit_code_list = [code_list.index(code) for code in combined_list]
            # Increment the co-occurrence count. We do double count here.
            for code_a in visit_code_list:
                for code_b in visit_code_list:
                    co_occ_matrix[code_a][code_b] += 1

    build_pmi_dct(co_occ_dct)

    co_occ_dct = sorted(co_occ_dct.items(), key=operator.itemgetter(1),
        reverse=True)
    write_scores_to_file('cooccurrence', co_occ_dct)

    return co_occ_matrix

def get_code_list():
    '''
    Returns the list of symptoms and herbs in order.
    '''
    code_list = []
    f = open('./results/code_list.txt', 'r')
    for line in f:
        code_list += [line.strip()]
    f.close()
    return code_list

def reduce_matrix(matrix, code_list, matrix_type):
    '''
    Given a co-occurrence matrix, perform SVD on it in order to to reduce the
    dimensionality of each medical code.
    '''
    U, s, Vh = svd(matrix)
    for k in [50, 100, 150]:
        top_indices = sorted(range(len(s)), key=lambda i: s[i])[-k:]
        # Get the top singular values.
        top_s = [s[i] for i in top_indices]

        reduced_Vh = []
        for row in Vh:
            row = [row[i] for i in top_indices]
            # Multiply the top singular values by each row in V_h.
            reduced_Vh += [np.array(row) * np.sqrt(top_s)]

        # Compute the pairwise cosine similarity.
        similarity_matrix = squareform(pdist(reduced_Vh, 'cosine'))

        similarity_dct = {}
        for row_i, row in enumerate(similarity_matrix):
            row_code = code_list[row_i]
            for col_i in range(row_i + 1, len(row)):
                col_code = code_list[col_i]
                similarity_dct[(row_code, col_code)] = 1 - row[col_i]
        # Sort the pairs of codes by their cosine simliarity.
        similarity_dct = sorted(similarity_dct.items(),
            key=operator.itemgetter(1), reverse=True)
        write_scores_to_file('%s_svd_k%d' % (matrix_type, k), similarity_dct)

def generate_first_time_dirs():
    '''
    Generate the folders for these baseline results.
    '''
    for model_type in ('co_svd_k50', 'co_svd_k100', 'co_svd_k150',
        'cooccurrence', 'pmi', 'pmi_svd_k50', 'pmi_svd_k100', 'pmi_svd_k150'):
        directory = './results/%s_baseline' % model_type
        if not os.path.exists(directory):
            os.makedirs(directory)

def co_occ_to_pmi_matrix(co_occ_matrix, code_list):
    '''
    Given the co-occurrence matrix, convert it to a PMI matrix.
    '''
    pmi_matrix = np.array(co_occ_matrix)

    code_count_dct = read_code_file('herb')
    code_count_dct.update(read_code_file('symptom'))

    # Divide the rows.
    for code_i, code in enumerate(code_list):
        code_count = code_count_dct[code]
        pmi_matrix[code_i] /= code_count
        pmi_matrix[:,code_i] /= code_count
    pmi_matrix[pmi_matrix == 0] = 1
    return np.log2(pmi_matrix)

def main():
    generate_first_time_dirs()
    patient_dct = get_patient_dct()
    code_list = read_code_list()
    co_occ_matrix = build_cooccurrence_matrix(patient_dct, code_list)
    pmi_matrix = co_occ_to_pmi_matrix(co_occ_matrix, code_list)
    
    print pmi_matrix[(code_list.index('少津'), code_list.index('天冬'))]

    exit()
    reduce_matrix(co_occ_matrix, code_list, 'co')
    reduce_matrix(pmi_matrix, code_list, 'pmi')


if __name__ == '__main__':
    start_time = time.time()
    main()
    print "---%f seconds---" % (time.time() - start_time)