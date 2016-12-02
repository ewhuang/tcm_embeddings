# tcm_embeddings

### Author: Edward Huang

### Project for machine translation between symptoms and herbs in TCM stomach data.


## Preprocessing

1.  Generates the preliminary results that shows the conditional probabilities
    of both symptoms on herbs and herbs on symptoms.

    ```bash
    $ python compute_conditional_probabilities.py
    ```


## med2vec Preliminary Testing

1.  Generate the input files from the stomach data into a file that med2vec
    can read. Creates two files, one for the baseline, and one for the test
    condition where each visit is separated into a symptom visit followed by
    an herb visit.

    ```bash
    $ python create_med2vec_input.py
    ```

2.  Find how many unique symptoms and herbs there are.
    
    ```bash
    $ python run_med2vec.py baseline/separated
    ```

3.  Run med2vec on our inputs.

    ```bash
    $ python run_med2vec.py baseline/separated pmi<optional>
    ```

    pmi optional argument optimizes pointwise mutual information instead of
    the default conditional probability of med2vec.

4.  Get the top 10 most similar pairs of vectors.

    ```bash
    $ python get_most_similar_med2vec_pairs.py baseline_epoch_num, separated_
                epoch_num pmi<optional>
    ```

    Generates a total of three documents per method type: one for the top
    herb-herb, herb-symptom, and symptom-symptom similarity scores.

5. Get the top similar pairs from a co-occurrence matrix into SVD baseline.

    ```bash
    $ python cooccurrence_svd_baseline.py
    ```
    

6. Run this after med2vec input in order to create the visit binary matrix.

    ```bash
    $ python visit_binary_matrix.py
    ```