# tcm_embeddings
Project for machine translation between symptoms and herbs in TCM stomach data.

### Author: Edward Huang

## Preprocessing

1.  Generates the preliminary results that shows the conditional probabilities
    of both symptoms on herbs and herbs on symptoms.

    ```bash
    $ python compute_conditional_probabilities.py
    ```


## med2vec Preliminary Testing
Must first grab the med2vec.py file from the [Edward Choi's GitHub](https://github.com/mp2893/med2vec)

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

5.  Get the top similar pairs from a co-occurrence matrix into SVD baseline.

    ```bash
    $ python cooccurrence_svd_baseline.py
    ```    

6. Run this after med2vec input in order to create the visit binary matrix.

    ```bash
    $ python visit_binary_matrix.py
    ```

## Experiments with Weighted Exclusivity Test (WExT)
Clone the repository from the [Raphael Group GitHub](https://github.com/raphael-group/wext) right into the folder.

1.  First, add code in ./wext/find_exclusive_sets.py. In line 194/195, we need
    to add an extra line to avoid an undefined variable error.

    ```python
    elif args.search_strategy == 'MCMC':
        method = nameToMethod[args.method]
    ```

2.  Runs WExt on the dataset.

    ```bash
    $ python weighted_exclusivity_most_similar_pairs.py set_size
    ```

    Outputs ./results/wext/3_set_output-sampled-sets-chinese.tsv
    where 3 can be replaced by set_size.