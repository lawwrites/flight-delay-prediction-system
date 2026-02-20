import pandas as pd
from step_b_import_data import DataLoader

class CleanData(DataLoader):
    def __init__(self, url, filename, filetype='csv'):
        super().__init__(url, filename, filetype) #Inherit DataLoader init
        self.dataframe = self.load_data() # Load data from DataLoader dataframe

    def dropIt(self):
        """Drop nulls and duplicates in the DataFrame."""
        nulls = self.dataframe.isnull().any().any()
        duplicates = self.dataframe.duplicated().any().any()
        if nulls:
            print("Dropping nulls...")
            self.dataframe.dropna(inplace=True)
        if duplicates:
            print("Dropping duplicates...")
            self.dataframe.drop_duplicates(inplace=True)
        return self  # return self for method chaining

    def strip_whitespace(self):
        """Strip whitespace from string columns in the DataFrame."""
        self.dataframe.columns = self.dataframe.columns.str.strip()
        for col in self.dataframe.columns:
            if self.dataframe[col].dtype == 'object':
                self.dataframe[col] = self.dataframe[col].str.strip()
        return self  # return self for method chaining
    
    def convert_time_columns(self):
        """Convert CRS_DEP_TIME, DEP_TIME, ARR_TIME into minutes since midnight."""
        for col in ['CRS_DEP_TIME', 'DEP_TIME', 'ARR_TIME']:
            if col in self.dataframe.columns:
                self.dataframe[col] = pd.to_datetime(
                    self.dataframe[col].dropna().astype(int).astype(str).str.zfill(4), 
                    format='%H%M', 
                    errors='coerce'
                )
                self.dataframe[col] = (
                    self.dataframe[col].dt.hour * 60 + self.dataframe[col].dt.minute
                )
        return self  # return self for method chaining
    
    def check(self):
        """Rport if nulls or duplicates remain."""
        isNull = self.dataframe.isnull().any().any()
        isDup = self.dataframe.duplicated().any().any()
        if isNull == False or isDup == False:
            print("Data contains no null and no duplicated values.")
        else:
            if isDup:
                print("Data contains duplicate rows.")
            if not isNull and not isDup:
                print("Data is clean: no nulls or duplicates found.")
        return self  # return self for method chaining

    def get_data(self):
        """Return the cleaned DataFrame."""
        return self.dataframe