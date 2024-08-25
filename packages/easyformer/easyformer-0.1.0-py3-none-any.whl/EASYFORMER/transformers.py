from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pandas as pd

from .encoders import CustomEncoder

def identify_columns(df):
    numerical_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
    return numerical_columns, categorical_columns

def create_pipeline(data):
    numerical_columns, categorical_columns = identify_columns(data)
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_columns),
            ('cat', CustomEncoder(), categorical_columns)
        ],
        remainder='drop'
    )
    
    pipeline = Pipeline(steps=[('preprocessor', preprocessor)])
    
    return pipeline
