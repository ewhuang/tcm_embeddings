### Author: Edward Huang

import subprocess
import sys
import time

### This script runs med2vec with the parameters we want. Automatically counts
### the number of unique medical codes for us.

def get_num_codes():
    '''
    Reads the code_list file and determines the number of unique symptoms and
    herbs we have in our dataset.
    '''
    num_codes = 0
    f = open('./results/code_list.txt', 'r')
    for line in f:
        num_codes += 1
    f.close()
    return num_codes

def main():
    if len(sys.argv) not in [3, 4]:
        print ('Usage:python %s model_type pmi<optional>' % sys.argv[0])
        exit()
    model_type = sys.argv[1]
    assert model_type in ['baseline', 'separated']
    pmi = ''
    if len(sys.argv) == 4:
        pmi = 'pmi_'

    visit_file = './results/med2vec_input_%s_visits.pickle' % model_type
    num_codes = get_num_codes()
    output_file = './results/med2vec_output/%s%s_model' % (pmi, model_type)

    command = 'python %smed2vec.py %s %d %s' % (pmi, visit_file, num_codes,
        output_file)
    subprocess.call(command, shell=True)

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))