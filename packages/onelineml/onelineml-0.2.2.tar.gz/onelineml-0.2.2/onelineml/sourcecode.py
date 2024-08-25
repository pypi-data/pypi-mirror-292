from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib

class CustomMissingValueImputer(BaseEstimator, TransformerMixin):
    def __init__(self, numerical_strategy='mean', categorical_strategy='most_frequent'):
        self.numerical_strategy = numerical_strategy
        self.categorical_strategy = categorical_strategy
        self.numeric_imputer = None
        self.categorical_imputer = None

    def fit(self, X, y=None):
        numerical_columns = X.select_dtypes(include=[np.number])
        categorical_columns = X.select_dtypes(include=[object, 'category'])
        
        if not numerical_columns.empty:
            self.numeric_imputer = SimpleImputer(strategy=self.numerical_strategy)
            self.numeric_imputer.fit(numerical_columns)
        
        if not categorical_columns.empty:
            self.categorical_imputer = SimpleImputer(strategy=self.categorical_strategy)
            self.categorical_imputer.fit(categorical_columns)
        
        return self

    def transform(self, X):
        numerical_columns = X.select_dtypes(include=[np.number])
        categorical_columns = X.select_dtypes(include=[object, 'category'])
        
        if not numerical_columns.empty:
            X_numeric = self.numeric_imputer.transform(numerical_columns)
            X_numeric_df = pd.DataFrame(X_numeric, columns=numerical_columns.columns)
        else:
            X_numeric_df = pd.DataFrame([], columns=numerical_columns.columns)
        
        if not categorical_columns.empty:
            X_categorical = self.categorical_imputer.transform(categorical_columns)
            X_categorical_df = pd.DataFrame(X_categorical, columns=categorical_columns.columns)
        else:
            X_categorical_df = pd.DataFrame([], columns=categorical_columns.columns)
        
        X_imputed = pd.concat([X_numeric_df, X_categorical_df], axis=1)
        return X_imputed[X.columns]

def model_factory(model_name, model_params):
    models = {
        'random_forest': RandomForestClassifier(random_state=42),
        'logistic_regression': LogisticRegression(random_state=42),
        'decision_tree': DecisionTreeClassifier(random_state=42),
        'svm': SVC(random_state=42),
        'knn': KNeighborsClassifier(),
        'xgboost': GradientBoostingClassifier(random_state=42),
        'naive_bayes': GaussianNB()
    }
    
    if model_name not in models:
        raise ValueError(f"Model '{model_name}' is not supported. Choose from {list(models.keys())}.")
    
    model = models[model_name]
    return model.set_params(**model_params)

def create_ml_pipeline(numerical_na_method, categorical_na_method, model_name, model_params, dataset, target, splitting_ratio=0.2):
    if isinstance(dataset, str):
        df = pd.read_csv(dataset)
    else:
        df = dataset
    
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in the dataset.")
    
    X = df.drop(columns=[target])
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=splitting_ratio, random_state=42)
    
    numerical_features = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = X.select_dtypes(include=[object, 'category']).columns.tolist()
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', Pipeline(steps=[
                ('imputer', CustomMissingValueImputer(numerical_strategy=numerical_na_method)), 
                ('scaler', StandardScaler())
            ]), numerical_features),
            
            ('cat', Pipeline(steps=[
                ('imputer', CustomMissingValueImputer(categorical_strategy=categorical_na_method)),
                ('onehot', OneHotEncoder(handle_unknown='ignore'))
            ]), categorical_features)
        ])
    
    model = model_factory(model_name, model_params)
    
    pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                               ('model', model)])
    
    pipeline.fit(X_train, y_train)
    
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    
    print(f"Model: {model_name}")
    print(f"Accuracy: {accuracy}")
    print(f"Classification Report:\n{report}")
    
    joblib.dump(pipeline, f'{model_name}_pipeline.pkl')
    
    return pipeline
