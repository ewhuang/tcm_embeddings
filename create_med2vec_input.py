#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

from collections import OrderedDict
from datetime import datetime
import cPickle
import os
import time

date_format = '%Y-%m-%d'

### This script writes out a file of the format stiupated by the med2vec page.
### https://github.com/mp2893/med2vec
### Uses the TCM data list to create the data matrix.
### Run time: 5.6 seconds.

def get_patient_dct():
    '''
    Returns dictionary
    Key: (name, date of birth) -> (str, str)
    Value: dictionary, where keys are (name, DOB) pairs and values are tuples
    containing the diseases, diagnosis dates, symptoms, and herbs of each visit.
    '''
    patient_dct = OrderedDict({})
    f = open('./data/HIS_tuple_word.txt', 'r')
    for i, line in enumerate(f):
        diseases, name, dob, diagnosis_date, symptoms, herbs = line.split('\t')
        if name == 'null' or dob == 'null':
            continue
        # Always ends with a colon, so the last element of the split will be
        # the empty string.
        disease_list = diseases.split(':')[:-1]
        
        diagnosis_date = diagnosis_date.split('，')[1][:len('xxxx-xx-xx')]
        # Format the diagnosis date.
        diagnosis_date = datetime.strptime(diagnosis_date, date_format)

        symptom_list = symptoms.split(':')[:-1]
        herb_list = herbs.split(':')[:-1]
        if len(symptom_list) == 0 or len(herb_list) == 0:
            continue

        # Add the listing to the dictionary.
        key = (name, dob)
        if key not in patient_dct:
            patient_dct[key] = {}
        patient_dct[key][diagnosis_date] = (disease_list, list(set(symptom_list
            )), list(set(herb_list)))
    f.close()

    return patient_dct

def get_symptom_and_herb_counts(patient_dct):
    '''
    Given the patient dictionary, count the symptom and herb occurrences in
    patients with more than one visit. Writes the counts out to file.
    Returns the list of unique medical codes.
    '''
    herb_count_dct, symptom_count_dct = {}, {}
    for key in patient_dct:
        visit_dct = patient_dct[key]
        if len(visit_dct) == 1:
            continue
        for date in visit_dct:
            disease_list, symptom_list, herb_list = visit_dct[date]

            # Update the counts of each symptom and herb.
            for symptom in symptom_list:
                if symptom not in symptom_count_dct:
                    symptom_count_dct[symptom] = 0
                symptom_count_dct[symptom] += 1
            for herb in herb_list:
                if herb not in herb_count_dct:
                    herb_count_dct[herb] = 0
                herb_count_dct[herb] += 1

    # Write out the unique symptoms and herbs to file.
    herb_out = open('./data/herb_count_dct.txt', 'w')
    for herb in herb_count_dct:
        herb_out.write('%s\t%d\n' % (herb, herb_count_dct[herb]))
    herb_out.close()

    symptom_out = open('./data/symptom_count_dct.txt', 'w')
    for symptom in symptom_count_dct:
        symptom_out.write('%s\t%d\n' % (symptom, symptom_count_dct[symptom]))
    symptom_out.close()

    return list(set(symptom_count_dct.keys()).union(herb_count_dct.keys()))

def make_pickle_list(patient_dct, code_list):
    '''
    Given a patient dictionary, make a list of lists. Each inner list 
    corresponds to a patient visit. The symptoms and herbs must be mapped to
    integers. Returns two list of lists. The second list makes each symptom
    set into a visit, and then an herb set into a following visit.
    '''
    pickle_list, double_pickle_list = [], []
    for key in patient_dct:
        visit_dct = patient_dct[key]
        # Skip patients that only had one visit.
        if len(visit_dct) == 1:
            continue
        for date in sorted(visit_dct.keys()):
            disease_list, symptom_list, herb_list = visit_dct[date]
            # Convert each symptom/herb to their index in the code list.
            symptom_list = [code_list.index(symp) for symp in symptom_list]
            herb_list = [code_list.index(herb) for herb in herb_list]
            # pickle_list is where each visit is all symptoms and herbs.
            pickle_list += [symptom_list + herb_list]
            # double_pickle_list is where each visit is separated into two
            # visits: a "symptom visit" and an "herb visit".
            double_pickle_list += [symptom_list]
            double_pickle_list += [herb_list]
        # A [-1] is the delimiter between patients.
        pickle_list += [[-1]]
        double_pickle_list += [[-1]]
    # Remove the last delimiter.
    return pickle_list[:-1], double_pickle_list[:-1]

def write_code_list(code_list):
    '''
    Writes out the code list to file, with one code occupying each line. This 
    way, we can find out what the resulting integers map to.
    '''
    out = open('./results/code_list.txt', 'w')
    for code in code_list:
        out.write('%s\n' % code)
    out.close()

def main():
    # patient_dct, code_list = get_patient_dct()
    patient_dct = get_patient_dct()
    code_list = get_symptom_and_herb_counts(patient_dct)
    pickle_list, double_pickle_list = make_pickle_list(patient_dct, code_list)

    with open('./results/med2vec_input_baseline.pickle', 'wb') as out:
        cPickle.dump(pickle_list, out)
    with open('./results/med2vec_input_separated_visits.pickle', 'wb') as out:
        cPickle.dump(double_pickle_list, out)

    write_code_list(code_list)

    med2vec_directory = './results/med2vec_output'
    if not os.path.exists(med2vec_directory):
        os.makedirs(med2vec_directory)

if __name__ == '__main__':
    start_time = time.time()
    main()
    print "---%f seconds---" % (time.time() - start_time)