from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
import numpy as np
import pandas as pd

class CustomMissingValueImputer(BaseEstimator, TransformerMixin):
    def __init__(self, numerical_strategy='mean', categorical_strategy='most_frequent'):
        self.numerical_strategy = numerical_strategy
        self.categorical_strategy = categorical_strategy
        self.numeric_imputer = None
        self.categorical_imputer = None

    def fit(self, X, y=None):
        self.numeric_imputer = SimpleImputer(strategy=self.numerical_strategy)
        self.categorical_imputer = SimpleImputer(strategy=self.categorical_strategy)
        
        self.numeric_imputer.fit(X.select_dtypes(include=[np.number]))
        self.categorical_imputer.fit(X.select_dtypes(include=[object, 'category']))
        return self

    def transform(self, X):
        X_numeric = self.numeric_imputer.transform(X.select_dtypes(include=[np.number]))
        X_categorical = self.categorical_imputer.transform(X.select_dtypes(include=[object, 'category']))
        
        X_imputed = np.hstack((X_numeric, X_categorical))
        return pd.DataFrame(X_imputed, columns=X.columns)
