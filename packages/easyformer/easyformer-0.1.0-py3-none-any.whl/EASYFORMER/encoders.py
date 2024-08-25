from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd

class CustomEncoder(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.encoders = {}
        
    def fit(self, X, y=None):
        for column in X.columns:
            if X[column].nunique() == 2:
                self.encoders[column] = LabelEncoder().fit(X[column])
            else:
                self.encoders[column] = OneHotEncoder(drop='first').fit(X[[column]])
        return self
    
    def transform(self, X):
        encoded_columns = []
        for column in X.columns:
            if column in self.encoders:
                if isinstance(self.encoders[column], LabelEncoder):
                    encoded_column = self.encoders[column].transform(X[column])
                    encoded_columns.append(pd.Series(encoded_column, name=column))
                else:
                    encoded_column = self.encoders[column].transform(X[[column]])
                    encoded_columns.append(pd.DataFrame(encoded_column.toarray(), 
                                                        columns=self.encoders[column].get_feature_names_out([column])))
        
        encoded_df = pd.concat(encoded_columns, axis=1)
        return encoded_df
