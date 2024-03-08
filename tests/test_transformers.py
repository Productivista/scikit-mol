# checking that the new transformers can work within a scikitlearn pipeline of the kind
# Pipeline([("s2m", SmilesToMol()), ("FP", FPTransformer()), ("RF", RandomForestRegressor())])
# using some test data stored in ./data/SLC6A4_active_excape_subset.csv

# to run as
# pytest tests/test_transformers.py --> tests/test_transformers.py::test_transformer PASSED


import pytest
import pandas as pd
from packaging.version import Version
import sklearn
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from scikit_mol.conversions import SmilesToMolTransformer
from scikit_mol.core import SKLEARN_VERSION_PANDAS_OUT
from scikit_mol.fingerprints import MACCSKeysFingerprintTransformer, RDKitFingerprintTransformer, AtomPairFingerprintTransformer, \
                                    TopologicalTorsionFingerprintTransformer, MorganFingerprintTransformer, SECFingerprintTransformer, \
                                    MHFingerprintTransformer, AvalonFingerprintTransformer


from fixtures import SLC6A4_subset, skip_pandas_output_test

def test_transformer(SLC6A4_subset):
    # load some toy data for quick testing on a small number of samples
    X_smiles, Y = SLC6A4_subset.SMILES, SLC6A4_subset.pXC50
    X_smiles = X_smiles.to_frame()
    X_train, X_test = X_smiles[:128], X_smiles[128:]
    Y_train, Y_test = Y[:128], Y[128:]

    # run FP with default parameters except when useCounts can be given as an argument
    FP_dict = {"MACCSTransformer": [MACCSKeysFingerprintTransformer, None],
               "RDKitFPTransformer": [RDKitFingerprintTransformer, None],
               "AtomPairFingerprintTransformer": [AtomPairFingerprintTransformer, False],
               "AtomPairFingerprintTransformer useCounts": [AtomPairFingerprintTransformer, True],
               "TopologicalTorsionFingerprintTransformer": [TopologicalTorsionFingerprintTransformer, False],
               "TopologicalTorsionFingerprintTransformer useCounts": [TopologicalTorsionFingerprintTransformer, True],
               "MorganTransformer": [MorganFingerprintTransformer, False],
               "MorganTransformer useCounts": [MorganFingerprintTransformer, True],
               "SECFingerprintTransformer": [SECFingerprintTransformer, None],
               "MHFingerprintTransformer": [MHFingerprintTransformer, None],
               'AvalonFingerprintTransformer': [AvalonFingerprintTransformer, None]}

    # fit on toy data and print train/test score if successful or collect the failed FP
    failed_FP = []
    for FP_name, (FP, useCounts) in FP_dict.items():
        try:
            print(f"\nrunning pipeline fitting and scoring for {FP_name} with useCounts={useCounts}")
            if useCounts is None:
                pipeline = Pipeline([("s2m", SmilesToMolTransformer()), ("FP", FP()), ("RF", RandomForestRegressor())])
            else:
                pipeline = Pipeline([("s2m", SmilesToMolTransformer()), ("FP", FP(useCounts=useCounts)), ("RF", RandomForestRegressor())])
            pipeline.fit(X_train, Y_train)
            train_score = pipeline.score(X_train, Y_train)
            test_score = pipeline.score(X_test, Y_test)
            print(f"\nfitting and scoring completed train_score={train_score}, test_score={test_score}")
        except:
            print(f"\n!!!! FAILED pipeline fitting and scoring for {FP_name} with useCounts={useCounts}")
            failed_FP.append(FP_name)
            pass

    # overall result
    assert len(failed_FP) == 0, f"the following FP have failed {failed_FP}"


@skip_pandas_output_test
def test_transformer_pandas_output(SLC6A4_subset, pandas_output):
    # load some toy data for quick testing on a small number of samples
    X_smiles = SLC6A4_subset.SMILES
    X_smiles = X_smiles.to_frame()

    # run FP with default parameters except when useCounts can be given as an argument
    FP_dict = {"MACCSTransformer": [MACCSKeysFingerprintTransformer, None],
               "RDKitFPTransformer": [RDKitFingerprintTransformer, None],
               "AtomPairFingerprintTransformer": [AtomPairFingerprintTransformer, False],
               "AtomPairFingerprintTransformer useCounts": [AtomPairFingerprintTransformer, True],
               "TopologicalTorsionFingerprintTransformer": [TopologicalTorsionFingerprintTransformer, False],
               "TopologicalTorsionFingerprintTransformer useCounts": [TopologicalTorsionFingerprintTransformer, True],
               "MorganTransformer": [MorganFingerprintTransformer, False],
               "MorganTransformer useCounts": [MorganFingerprintTransformer, True],
               "SECFingerprintTransformer": [SECFingerprintTransformer, None],
               "MHFingerprintTransformer": [MHFingerprintTransformer, None],
               'AvalonFingerprintTransformer': [AvalonFingerprintTransformer, None]}

    # fit on toy data and check that the output is a pandas dataframe
    failed_FP = []
    for FP_name, (FP, useCounts) in FP_dict.items():
        try:
            print(f"\nrunning pipeline fitting and scoring for {FP_name} with useCounts={useCounts}")
            if useCounts is None:
                pipeline = Pipeline([("s2m", SmilesToMolTransformer()), ("FP", FP())])
            else:
                pipeline = Pipeline([("s2m", SmilesToMolTransformer()), ("FP", FP(useCounts=useCounts))])
            pipeline.fit(X_smiles)
            X_transformed = pipeline.transform(X_smiles)
            assert isinstance(X_transformed, pd.DataFrame), f"the output of {FP_name} is not a pandas dataframe"
            assert X_transformed.shape[0] == len(X_smiles), f"the number of rows in the output of {FP_name} is not equal to the number of samples"
            assert len(X_transformed.columns) == pipeline.named_steps["FP"].nBits, f"the number of columns in the output of {FP_name} is not equal to the number of bits"
            print(f"\nfitting and transforming completed")

        except:
            print(f"\n!!!! FAILED pipeline fitting and transforming for {FP_name} with useCounts={useCounts}")
            failed_FP.append(FP_name)
            pass

    # overall result
    assert len(failed_FP) == 0, f"the following FP have failed pandas transformation {failed_FP}"






