# tcm_embeddings
TCM project with embeddings.

Author: Edward Huang

Project for machine translation between symptoms and herbs in TCM stomach data.


_________________________________PREPROCESSING__________________________________

1.  Generates the preliminary results that shows the conditional probabilities
    of both symptoms on herbs and herbs on symptoms.

    $ python compute_conditional_probabilities.py


___________________________MED2VEC PRELIMINARY TESTING_________________________

1.  Generate the input files from the stomach data into a file that med2vec
    can read. Creates two files, one for the baseline, and one for the test
    condition where each visit is separated into a symptom visit followed by
    an herb visit.

    $ python create_med2vec_input.py

2.  Find how many unique symptoms and herbs there are.
    
    $ wc -ll ./results/code_list.txt

3.  This output becomes num_codes. Run med2vec on our inputs.

    $ python med2vec.py ./results/med2vec_input_baseline.pickle num_codes
                            ./results/med2vec_output/%s_model % (baseline,
                                                            separated)
    $ python pmi_med2vec.py ...

    Same input as med2vec.py. We optimize PMI instead of the conditional
    probability for word embeddings (equation 4 of the med2vec paper).

4.  Get the top 10 most similar pairs of vectors.

    $ python get_most_similar_med2vec_pairs.py baseline_epoch_num, separated_
                epoch_num pmi<optional>

    Generates a total of three documents per method type: one for the top
    herb-herb, herb-symptom, and symptom-symptom similarity scores.

5. Get the top similar pairs from a co-occurrence matrix into SVD baseline.

    $ python cooccurrence_svd_baseline.py
    

6. Run this after med2vec input in order to create the visit binary matrix.

    $ python visit_binary_matrix.py