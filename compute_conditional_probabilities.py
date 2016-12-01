#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

from datetime import datetime
import operator
import time
import sys
import csv

### This script finds the conditional probabilities of sequential herb/symptom
### interactions. Finds the probability of an herb given a symptom as well
### as the probability of a symptom given an herb.

date_format = '%Y-%m-%d'

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
        # Add the listing to the dictionary.
        key = (name, dob)
        if key not in patient_dct:
            patient_dct[key] = {}
        patient_dct[key][diagnosis_date] = (disease_list, symptom_list,
            herb_list)
    f.close()
    return patient_dct

def get_individual_patient_counts(visit_dct, herb_given_symptom_count_dct,
    herb_given_new_symptom_count_dct, symptom_count_dct, new_symptom_count_dct):
    '''
    Updates the two dictionaries.

    Key: (herb/symptom, symptom/herb) pair -> (str, str)
    Value: number of times the sequence appears in the visit -> int

    Key: medical code (herb or symptom) -> str
    Value: number of times the code appears in all visits -> int
    '''
    def increment_dictionary(dct, key):
        if key in dct:
            dct[key] += 1.0
        else:
            dct[key] = 1.0

    date_list = visit_dct.keys()
    date_list.sort()
    # Initialize the herbs prescribed in the previous visit.
    previous_herb_list, previous_symptom_list = [], []
    for date in date_list:
        disease_list, symptom_list, herb_list = visit_dct[date]
        # Determine which herbs are newly prescribed.
        new_herb_set = set(herb_list).difference(previous_herb_list)
        # Compute the dependency counts of new herbs given all symptoms.
        for symptom in symptom_list:
            # Also increment the symptom counts.
            increment_dictionary(symptom_count_dct, symptom)
            for herb in new_herb_set:
                increment_dictionary(herb_given_symptom_count_dct, (herb,
                    symptom))
        # Compute the dependecy counts of new herbs given new symptoms.
        new_symptom_set = set(symptom_list).difference(previous_symptom_list)
        for symptom in new_symptom_set:
            increment_dictionary(new_symptom_count_dct, symptom)
            for herb in new_herb_set:
                increment_dictionary(herb_given_new_symptom_count_dct, (herb,
                    symptom))

        # Update the symptoms and herbs from the previous visit.
        previous_herb_list = herb_list[:]
        previous_symptom_list = symptom_list[:]

def normalize_count_dct(herb_given_symptom_count_dct, symptom_count_dct):
    '''
    Divides each entry of a dictionary by the count of its key's second value.
    '''
    conditional_prob_dct = {}
    for key in herb_given_symptom_count_dct:
        # This is the number of times that the symptom occurs.
        p_b = symptom_count_dct[key[1]]
        # Skip symptoms that appear in fewer than 10 visits.
        if p_b < 10:
            continue
        conditional_prob_dct[key] = herb_given_symptom_count_dct[key] / p_b
    return conditional_prob_dct

def write_conditional_probabilities(herb_given_symptom_prob_dct, fname):
    '''
    Sort the conditional count dictionary, and write it out to file.
    '''
    sorted_count = sorted(herb_given_symptom_prob_dct.items(),
        key=operator.itemgetter(1), reverse=True)
    out = open('./results/%s.txt' % fname, 'w')
    for (herb, symptom), prob in sorted_count:
        out.write('%s\t%s\t%f\n' % (herb, symptom, prob))
    out.close()

def compute_conditional_probabilities(patient_dct):
    '''
    Goes through each patient's visits sequentially, and determines the
    probability of each herb-symptom and symptom-herb sequence.
    '''
    herb_given_symptom_count_dct, herb_given_new_symptom_count_dct = {}, {}
    symptom_count_dct, new_symptom_count_dct = {}, {}
    for (name, dob) in patient_dct:
        visit_dct = patient_dct[(name, dob)]
        # Skip patient records that only have one visit.
        if len(visit_dct) == 1:
            continue
        # Update the dictionaries.
        get_individual_patient_counts(visit_dct, herb_given_symptom_count_dct,
            herb_given_new_symptom_count_dct, symptom_count_dct,
            new_symptom_count_dct)

    # Normalize the counts.
    herb_given_symptom_prob_dct = normalize_count_dct(
        herb_given_symptom_count_dct, symptom_count_dct)
    herb_given_new_symptom_prob_dct = normalize_count_dct(
        herb_given_new_symptom_count_dct, new_symptom_count_dct)

    write_conditional_probabilities(herb_given_symptom_prob_dct,
        'herb_given_symptom')

    write_conditional_probabilities(herb_given_new_symptom_prob_dct,
        'herb_given_new_symptom')

def main():
    patient_dct = get_patient_dct()
    compute_conditional_probabilities(patient_dct)

if __name__ == '__main__':
    start_time = time.time()
    main()
    print "---%f seconds---" % (time.time() - start_time)