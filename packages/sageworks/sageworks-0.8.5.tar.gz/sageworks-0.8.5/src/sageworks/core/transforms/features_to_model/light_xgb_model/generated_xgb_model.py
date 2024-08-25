# Imports for XGB Model
import xgboost as xgb
import awswrangler as wr

# Model Performance Scores
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    mean_squared_error,
    precision_recall_fscore_support,
    confusion_matrix,
)

# Classification Encoder
from sklearn.preprocessing import LabelEncoder

# Scikit Learn Imports
from sklearn.model_selection import train_test_split

from io import StringIO
import json
import argparse
import joblib
import os
import pandas as pd
from typing import List


# Function to check if dataframe is empty
def check_dataframe(df: pd.DataFrame, df_name: str) -> None:
    """
    Check if the provided dataframe is empty and raise an exception if it is.

    Args:
        df (pd.DataFrame): DataFrame to check
        df_name (str): Name of the DataFrame
    """
    if df.empty:
        msg = f"*** The training data {df_name} has 0 rows! ***STOPPING***"
        print(msg)
        raise ValueError(msg)


def expand_proba_column(df: pd.DataFrame, class_labels: List[str]) -> pd.DataFrame:
    """
    Expands a column in a DataFrame containing a list of probabilities into separate columns.

    Args:
        df (pd.DataFrame): DataFrame containing a "pred_proba" column
        class_labels (List[str]): List of class labels

    Returns:
        pd.DataFrame: DataFrame with the "pred_proba" expanded into separate columns
    """

    # Sanity check
    proba_column = "pred_proba"
    if proba_column not in df.columns:
        raise ValueError('DataFrame does not contain a "pred_proba" column')

    # Construct new column names with '_proba' suffix
    new_col_names = [f"{label}_proba" for label in class_labels]

    # Expand the proba_column into separate columns for each probability
    proba_df = pd.DataFrame(df[proba_column].tolist(), columns=new_col_names)

    # Drop the original proba_column and reset the index in prep for the concat
    df = df.drop(columns=[proba_column])
    df = df.reset_index(drop=True)

    # Concatenate the new columns with the original DataFrame
    df = pd.concat([df, proba_df], axis=1)
    print(df)
    return df


if __name__ == "__main__":
    """The main function is for training the XGBoost model"""

    # Harness Template Parameters
    target = "class"
    feature_list = ["bcut2d_logplow", "numradicalelectrons", "smr_vsa5", "fr_lactam", "fr_morpholine", "fr_aldehyde", "slogp_vsa1", "fr_amidine", "bpol", "fr_ester", "fr_azo", "kappa3", "peoe_vsa5", "fr_ketone_topliss", "vsa_estate9", "estate_vsa9", "bcut2d_mrhi", "fr_ndealkylation1", "numrotatablebonds", "minestateindex", "fr_quatn", "peoe_vsa3", "fr_epoxide", "fr_aniline", "minpartialcharge", "fr_nitroso", "fpdensitymorgan2", "fr_oxime", "fr_sulfone", "smr_vsa1", "kappa1", "fr_pyridine", "numaromaticrings", "vsa_estate6", "molmr", "estate_vsa1", "fr_dihydropyridine", "vsa_estate10", "fr_alkyl_halide", "chi2n", "fr_thiocyan", "fpdensitymorgan1", "fr_unbrch_alkane", "slogp_vsa9", "chi4n", "fr_nitro_arom", "fr_al_oh", "fr_furan", "fr_c_s", "peoe_vsa8", "peoe_vsa14", "numheteroatoms", "fr_ndealkylation2", "maxabspartialcharge", "vsa_estate2", "peoe_vsa7", "apol", "numhacceptors", "fr_tetrazole", "vsa_estate1", "peoe_vsa9", "naromatom", "bcut2d_chghi", "fr_sh", "fr_halogen", "slogp_vsa4", "fr_benzodiazepine", "molwt", "fr_isocyan", "fr_prisulfonamd", "maxabsestateindex", "minabsestateindex", "peoe_vsa11", "slogp_vsa12", "estate_vsa5", "numaliphaticcarbocycles", "bcut2d_mwlow", "slogp_vsa7", "fr_allylic_oxid", "fr_methoxy", "fr_nh0", "fr_coo2", "fr_phenol", "nacid", "nbase", "chi3v", "fr_ar_nh", "fr_nitrile", "fr_imidazole", "fr_urea", "bcut2d_mrlow", "chi1", "smr_vsa6", "fr_aryl_methyl", "narombond", "fr_alkyl_carbamate", "fr_piperzine", "exactmolwt", "qed", "chi0n", "fr_sulfonamd", "fr_thiazole", "numvalenceelectrons", "fr_phos_acid", "peoe_vsa12", "fr_nh1", "fr_hdrzine", "fr_c_o_nocoo", "fr_lactone", "estate_vsa6", "bcut2d_logphi", "vsa_estate7", "peoe_vsa13", "numsaturatedcarbocycles", "fr_nitro", "fr_phenol_noorthohbond", "rotratio", "fr_barbitur", "fr_isothiocyan", "balabanj", "fr_arn", "fr_imine", "maxpartialcharge", "fr_sulfide", "slogp_vsa11", "fr_hoccn", "fr_n_o", "peoe_vsa1", "slogp_vsa6", "heavyatommolwt", "fractioncsp3", "estate_vsa8", "peoe_vsa10", "numaliphaticrings", "fr_thiophene", "maxestateindex", "smr_vsa10", "labuteasa", "smr_vsa2", "fpdensitymorgan3", "smr_vsa9", "slogp_vsa10", "numaromaticheterocycles", "fr_nh2", "fr_diazo", "chi3n", "fr_ar_coo", "slogp_vsa5", "fr_bicyclic", "fr_amide", "estate_vsa10", "fr_guanido", "chi1n", "numsaturatedrings", "fr_piperdine", "fr_term_acetylene", "estate_vsa4", "slogp_vsa3", "fr_coo", "fr_ether", "estate_vsa7", "bcut2d_chglo", "fr_oxazole", "peoe_vsa6", "hallkieralpha", "peoe_vsa2", "chi2v", "nocount", "vsa_estate5", "fr_nhpyrrole", "fr_al_coo", "bertzct", "estate_vsa11", "minabspartialcharge", "slogp_vsa8", "fr_imide", "kappa2", "numaliphaticheterocycles", "numsaturatedheterocycles", "fr_hdrzone", "smr_vsa4", "fr_ar_n", "nrot", "smr_vsa8", "slogp_vsa2", "chi4v", "fr_phos_ester", "fr_para_hydroxylation", "smr_vsa3", "nhohcount", "estate_vsa2", "mollogp", "tpsa", "fr_azide", "peoe_vsa4", "numhdonors", "fr_al_oh_notert", "fr_c_o", "chi0", "fr_nitro_arom_nonortho", "vsa_estate3", "fr_benzene", "fr_ketone", "vsa_estate8", "smr_vsa7", "fr_ar_oh", "fr_priamide", "ringcount", "estate_vsa3", "numaromaticcarbocycles", "bcut2d_mwhi", "chi1v", "heavyatomcount", "vsa_estate4", "chi0v"]
    model_type = "classifier"
    model_metrics_s3_path = "s3://ideaya-sageworks-bucket/models/training/test-dq-sol-100-class"
    train_all_data = "True"
    validation_split = 0.2

    # Sagemaker specific arguments. Defaults are set in the environment variables.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-data-dir", type=str, default=os.environ["SM_OUTPUT_DATA_DIR"]
    )
    parser.add_argument("--model-dir", type=str, default=os.environ["SM_MODEL_DIR"])
    parser.add_argument("--train", type=str, default=os.environ["SM_CHANNEL_TRAIN"])
    args = parser.parse_args()

    # Read the training data into DataFrames
    training_files = [
        os.path.join(args.train, file)
        for file in os.listdir(args.train)
        if file.endswith(".csv")
    ]
    print(f"Training Files: {training_files}")

    # Combine files and read them all into a single pandas dataframe
    all_df = pd.concat([pd.read_csv(file, engine="python") for file in training_files])

    # Check if the dataframe is empty
    check_dataframe(all_df, "training_df")

    # Features/Target output
    print(f"Target: {target}")
    print(f"Features: {str(feature_list)}")

    # Do we want to train on all the data?
    if train_all_data == "True":
        print("Training on ALL of the data")
        df_train = all_df.copy()
        df_val = all_df.copy()

    # Does the dataframe have a training column?
    elif "training" in all_df.columns:
        print("Found training column, splitting data based on training column")
        df_train = all_df[all_df["training"] == 1].copy()
        df_val = all_df[all_df["training"] == 0].copy()
    else:
        # Just do a random training Split
        print("WARNING: No training column found, splitting data with random state=42")
        df_train, df_val = train_test_split(
            all_df, test_size=validation_split, random_state=42
        )
    print(f"FIT/TRAIN: {df_train.shape}")
    print(f"VALIDATION: {df_val.shape}")

    # Now spin up our XGB Model
    if model_type == "classifier":
        xgb_model = xgb.XGBClassifier()

        # Encode the target column
        label_encoder = LabelEncoder()
        df_train[target] = label_encoder.fit_transform(df_train[target])
        df_val[target] = label_encoder.transform(df_val[target])

    else:
        xgb_model = xgb.XGBRegressor()
        label_encoder = None  # We don't need this for regression

    # Grab our Features, Target and Train the Model
    y = df_train[target]
    X = df_train[feature_list]
    xgb_model.fit(X, y)

    # Make Predictions on the Validation Set
    print(f"Making Predictions on Validation Set...")
    preds = xgb_model.predict(df_val[feature_list])
    if model_type == "classifier":
        # Also get the probabilities for each class
        print("Processing Probabilities...")
        probs = xgb_model.predict_proba(df_val[feature_list])
        df_val["pred_proba"] = [p.tolist() for p in probs]

        # Expand the pred_proba column into separate columns for each class
        print(df_val.columns)
        df_val = expand_proba_column(df_val, label_encoder.classes_)
        print(df_val.columns)

        # Decode the target and prediction labels
        df_val[target] = label_encoder.inverse_transform(df_val[target])
        preds = label_encoder.inverse_transform(preds)

    # Save predictions to S3 (just the target, prediction, and '_proba' columns)
    df_val["prediction"] = preds
    output_columns = [target, "prediction"]
    output_columns += [col for col in df_val.columns if col.endswith("_proba")]
    wr.s3.to_csv(
        df_val[output_columns],
        path=f"{model_metrics_s3_path}/validation_predictions.csv",
        index=False,
    )

    # Report Performance Metrics
    if model_type == "classifier":
        # Get the label names and their integer mapping
        label_names = label_encoder.classes_

        # Calculate various model performance metrics
        scores = precision_recall_fscore_support(
            df_val[target], preds, average=None, labels=label_names
        )

        # Put the scores into a dataframe
        score_df = pd.DataFrame(
            {
                target: label_names,
                "precision": scores[0],
                "recall": scores[1],
                "fscore": scores[2],
                "support": scores[3],
            }
        )

        # We need to get creative with the Classification Metrics
        metrics = ["precision", "recall", "fscore", "support"]
        for t in label_names:
            for m in metrics:
                value = score_df.loc[score_df[target] == t, m].iloc[0]
                print(f"Metrics:{t}:{m} {value}")

        # Compute and output the confusion matrix
        conf_mtx = confusion_matrix(df_val[target], preds, labels=label_names)
        for i, row_name in enumerate(label_names):
            for j, col_name in enumerate(label_names):
                value = conf_mtx[i, j]
                print(f"ConfusionMatrix:{row_name}:{col_name} {value}")

    else:
        # Calculate various model performance metrics (regression)
        rmse = mean_squared_error(df_val[target], preds, squared=False)
        mae = mean_absolute_error(df_val[target], preds)
        r2 = r2_score(df_val[target], preds)
        print(f"RMSE: {rmse:.3f}")
        print(f"MAE: {mae:.3f}")
        print(f"R2: {r2:.3f}")
        print(f"NumRows: {len(df_val)}")

    # Now save the model to the standard place/name
    xgb_model.save_model(os.path.join(args.model_dir, "xgb_model.json"))
    if label_encoder:
        joblib.dump(label_encoder, os.path.join(args.model_dir, "label_encoder.joblib"))

    # Also save the features (this will validate input during predictions)
    with open(os.path.join(args.model_dir, "feature_columns.json"), "w") as fp:
        json.dump(feature_list, fp)


def model_fn(model_dir):
    """Deserialized and return fitted model"""

    # Load our XGBoost model from the model directory
    model_path = os.path.join(model_dir, "xgb_model.json")
    with open(model_path, "r") as f:
        model_json = json.load(f)
    saved_model_type = json.loads(model_json.get('learner').get('attributes').get('scikit_learn')).get('_estimator_type')
    if saved_model_type == "classifier":
        model = xgb.XGBClassifier()
    elif saved_model_type == "regressor":
        model = xgb.XGBRegressor()
    else:
        msg = f"Model type ({saved_model_type}) not recognized. Expected 'classifier' or 'regressor'"
        raise ValueError(msg)

    model.load_model(model_path)
    return model


def model_fn_fake(model_dir):
    """Fake model_fn for testing endpoint creation."""

    class DummyModel:
        def predict(self, data):
            return [0] * len(data)

    return DummyModel()


def input_fn(input_data, content_type):
    """We only take CSV Input"""
    if content_type == "text/csv":
        # Read the input buffer as a CSV file.
        input_df = pd.read_csv(StringIO(input_data))
        return input_df
    else:
        raise ValueError(f"{content_type} not supported by script!")


def output_fn(output_df, accept_type):
    """We only give CSV Output"""
    if accept_type == "text/csv":
        return output_df.to_csv(index=False), "text/csv"  # Return a CSV String and the content type
    else:
        raise RuntimeError(
            f"{accept_type} accept type is not supported by this script."
        )


def predict_fn(df, model):
    """Make Predictions with our XGB Model"""

    # Grab our feature columns (from training)
    model_dir = os.environ["SM_MODEL_DIR"]
    with open(os.path.join(model_dir, "feature_columns.json")) as fp:
        features = json.load(fp)
    print(f"Features: {features}")

    # Load our Label Encoder if we have one
    label_encoder = None
    if os.path.exists(os.path.join(model_dir, "label_encoder.joblib")):
        label_encoder = joblib.load(os.path.join(model_dir, "label_encoder.joblib"))

    # Predict the features against our XGB Model
    predictions = model.predict(df[features])

    # If we have a label encoder, decode the predictions
    if label_encoder:
        predictions = label_encoder.inverse_transform(predictions)

    # Set the predictions on the DataFrame
    df["prediction"] = predictions

    # Does our model have a 'predict_proba' method? If so we will call it and add the results to the DataFrame
    if getattr(model, "predict_proba", None):
        probs = model.predict_proba(df[features])
        df["pred_proba"] = [p.tolist() for p in probs]

        # Expand the pred_proba column into separate columns for each class
        df = expand_proba_column(df, label_encoder.classes_)

    # All done, return the DataFrame
    return df
