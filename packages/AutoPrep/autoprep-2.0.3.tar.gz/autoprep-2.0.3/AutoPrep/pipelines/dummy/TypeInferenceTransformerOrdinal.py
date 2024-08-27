# %%
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.compose import make_column_selector
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.utils.validation import check_array, check_is_fitted

import warnings

# Warnungen vom Versuch des castens ignorieren
warnings.filterwarnings("ignore")

from sklearn import set_config

set_config(transform_output="pandas")


class TypeInferenceTransformerOrdinal(BaseEstimator, TransformerMixin):
    """
    SchemaTransformer for a certain Pandas DataFrame input.

    Steps:
        (1) Attempt to convert object columns into a better data type format.\n
        (2) Attempt to convert columns with a time series schema into the correct data type.\n
        (3) Attempt to convert numerical data with the incorrect data type into the correct data type.\n
            Example: "col1": [1, "2", 3]  to "col1": [1, 2, 3]\n
        (4) NaN values are formatted correctly for subsequent processing.\n
        (5) Return of the adjusted dataframe.\n


    Parameters
    ----------
    datetime_columns : list
        List of certain Time-Columns that should be converted in timestamp data types.

    exclude_columns : list
        List of Columns that will be dropped.

    name_transformer : list
        Is used for the output, so the enduser can check what Columns are used for a certain Transformation.

    ordinal_columns : list
        Only ordinal_columns will be transformed.

    """

    def __init__(
        self,
        datetime_columns=None,
        exclude_columns: list = None,
        ordinal_columns: list = None,
        name_transformer="",
    ):
        self.datetime_columns = datetime_columns
        self.ordinal_columns = ordinal_columns

        self.exclude_columns = exclude_columns
        self.feature_names = None
        self.name_transformer = name_transformer

    def convert_schema_nans(self, X):
        X_Copy = X.copy()

        for col in X_Copy.columns:
            X_Copy[col] = X_Copy[col].replace("NaN", np.nan)
            X_Copy[col] = X_Copy[col].replace("nan", np.nan)
            X_Copy[col] = X_Copy[col].replace(" ", np.nan)
            X_Copy[col] = X_Copy[col].replace("", np.nan)
        return X_Copy

    def infer_schema_X(self, X_copy):
        try:
            X_copy = X_copy.infer_objects()
        except:
            pass

        for col in X_copy.columns:
            if X_copy[col].dtype == "object":
                if self.datetime_columns is not None and col in self.datetime_columns:
                    try:
                        X_copy[col] = pd.to_datetime(
                            X_copy[col], infer_datetime_format=True, errors="coerce"
                        )
                        # print("\nColumns to time dtype:", col, "\n")
                    except:
                        pass
                else:
                    try:
                        X_copy[col] = pd.to_datetime(
                            X_copy[col], infer_datetime_format=True
                        )
                        # print("\nColumns to time dtype:", col, "\n")
                    except:
                        pass

                try:
                    X_copy[col] = X_copy[col].astype(np.float64)
                    # print("\nColumns to numeric dtype:", col, "\n")
                except (ValueError, TypeError):
                    pass

        X_copy.convert_dtypes()

        return X_copy

    def fit(self, X, y=None):
        return self

    def transform(self, X) -> pd.DataFrame:
        
        X = X[self.ordinal_columns]

        if self.exclude_columns is not None:
            for col in self.exclude_columns:
                try:
                    X.drop([col], axis=1, inplace=True)
                except:
                    print(f"Column {col} could not be dropped.")

        self.feature_names = X.columns

        X_copy = X.copy()
        X_copy = self.convert_schema_nans(X_copy)

        X_copy = self.infer_schema_X(X_copy=X_copy)

        print(f"\n\nDtypes-Schema / Columns {self.name_transformer}:\n")
        print(X_copy.dtypes, "\n")

        X_copy = X_copy.astype(str)

        return X_copy

    def get_feature_names(self, input_features=None):
        return self.feature_names


