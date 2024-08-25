from .models import model_factory
from .preprocessing import CustomMissingValueImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import pandas as pd

def create_ml_pipeline(numerical_na_method, categorical_na_method, model_name, model_params, dataset, target, splitting_ratio=0.2):
    df = pd.read_csv(dataset)
    
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
