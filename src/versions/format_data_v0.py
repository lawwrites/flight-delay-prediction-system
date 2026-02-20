import pandas as pd
from import_data import DataLoader

class CleanData:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def check(self):
        """Check for nulls and duplicates in the DataFrame."""
        nulls = self.dataframe.isnull().any().any()
        duplicates = self.dataframe.duplicated().any().any()
        return nulls, duplicates
    
    def strip_whitespace(self):
        """Strip whitespace from string columns in the DataFrame."""
        self.dataframe.columns = self.dataframe.columns.str.strip()
        for col in self.dataframe.columns:
            if self.dataframe[col].dtype == 'object':
                self.dataframe[col] = self.dataframe[col].str.strip()
        return self.dataframe
    
    def convert_time_columns(self):
        """Convert CRS_DEP_TIME, DEP_TIME, ARR_TIME into minutes since midnight."""
        for col in ['CRS_DEP_TIME', 'DEP_TIME', 'ARR_TIME']:
            if col in self.dataframe.columns:
                self.dataframe[col] = pd.to_datetime(
                    self.dataframe[col].dropna().astype(int).astype(str).str.zfill(4), 
                    format='%H%M', 
                    errors='coerce'
                )
                # Convert to total minutes
                self.dataframe[col] = self.dataframe[col].dt.hour * 60 + self.dataframe[col].dt.minute
        return self.dataframe
