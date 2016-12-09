#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

import numpy as np
import operator
import os
from scipy.spatial.distance import pdist, squareform
import sys
import time

### Reads the embedding vectors created by med2vec and then outputs files
### that show the most similar pairs of medical codes.
### Run time: 30 seconds.

def read_npz_file(last_epoch, model_type):
    '''
    Given the string of a last epoch number, read the file for a given med2vec
    run.
    '''
    assert (model_type in ['baseline', 'separated', 'pmi_baseline',
        'pmi_separated'])
    data = np.load('./results/med2vec_output/%s_model.%s.npz' % (
        model_type, last_epoch))
    return data

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

def write_most_similar_pairs(data, code_list, model_type):
    '''
    Given a data list, get the embeddings for each element, and find the
    similarity scores for each pair. Write them out to file.
    '''
    embedding_matrix = data['W_emb']
    # Compute pairwise cosine similarity.
    similarity_matrix = squareform(pdist(embedding_matrix, 'cosine'))

    assert len(similarity_matrix) == len(embedding_matrix)

    similarity_dct = {}
    for row_i, row in enumerate(similarity_matrix):
        row_code = code_list[row_i]
        for col_i in range(row_i + 1, len(row)):
            col_code = code_list[col_i]
            similarity_dct[(row_code, col_code)] = 1 - row[col_i]
    # Sort the pairs of codes by their cosine simliarity.
    similarity_dct = sorted(similarity_dct.items(), key=operator.itemgetter(1),
        reverse=True)

    herb_count_dct = read_code_file('herb')
    symptom_count_dct = read_code_file('symptom')

    # We only want 1000 of herb-herb, symptom-symptom, and herb-symptoms.
    hh_count, ss_count, hs_count = 0, 0, 0

    # Write out to one of three files.
    folder = './results/med2vec_baseline'
    ss_out = open('%s/%s_ss_pair_similarities.txt' % (folder, model_type), 'w')
    hs_out = open('%s/%s_hs_pair_similarities.txt' % (folder, model_type), 'w')
    hh_out = open('%s/%s_hh_pair_similarities.txt' % (folder, model_type), 'w')
    for (code_a, code_b), cosine in similarity_dct:
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
        out_str = '%s\t%s\t%f\t%d\t%d\n' % (code_a, code_b, cosine, a_count,
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

def generate_folders():
    directory = './results/med2vec_baseline'
    if not os.path.exists(directory):
        os.makedirs(directory)

def main():
    if len(sys.argv) not in [3, 4]:
        print ('Usage: python %s <baseline_last_epoch>'
            '<separated_last_epcoh> pmi<optional>' % sys.argv[0])
        exit()
    baseline_last_epoch, separated_last_epcoh = sys.argv[1], sys.argv[2]

    baseline_name = 'baseline'
    separated_name = 'separated'

    if len(sys.argv) == 4:
        baseline_name = 'pmi_' + baseline_name
        separated_name = 'pmi_' + separated_name

    generate_folders()

    baseline_data = read_npz_file(baseline_last_epoch, baseline_name)
    separated_data = read_npz_file(separated_last_epcoh, separated_name)

    code_list = get_code_list()
    write_most_similar_pairs(baseline_data, code_list, baseline_name)
    write_most_similar_pairs(separated_data, code_list, separated_name)

if __name__ == '__main__':
    start_time = time.time()
    main()
    print "---%f seconds---" % (time.time() - start_time)