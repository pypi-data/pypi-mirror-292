from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

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
