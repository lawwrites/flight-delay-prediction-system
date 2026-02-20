import pandas as pd
import numpy as np
import os
from datetime import date

class DataLoader:
    today = date.today() 
    def __init__(self, url, filename, filetype='csv'):
        self.url = url
        self.filename = filename
        self.filetype = filetype
        self.filepath = os.path.join(url, filename)
        self.dataframe = None   # always store dataset here

    def load_data(self):
        """Load dataset into self.dataframe."""
        try:
            if self.filetype == 'csv':
                self.dataframe = pd.read_csv(self.filepath)
            elif self.filetype == 'excel':
                self.dataframe = pd.read_excel(self.filepath)
            else:
                raise ValueError("Unsupported file type. Use 'csv' or 'excel'.")
        except FileNotFoundError:
            raise FileNotFoundError(f"File {self.filepath} not found.")
        except Exception as e:
            raise RuntimeError(f"Error loading data: {e}")
        return self.dataframe

    def save_data(self, dataframe=None):
        """Save self.dataframe back to file."""
        df_to_save = dataframe if dataframe is not None else self.dataframe
        try:
            if self.dataframe is None:
                raise ValueError("No dataframe loaded. Run load_data() first.")
            
            if self.filetype == 'csv':
                self.dataframe.to_csv(self.filepath, index=False)
            elif self.filetype == 'excel':
                self.dataframe.to_excel(self.filepath, index=False)
            else:
                raise ValueError("Unsupported file type. Use 'csv' or 'excel'.")
        except Exception as e:
            raise RuntimeError(f"Error saving data: {e}")
        
    def save_versions(self, dataframe=None, version=None):
        """Save self.dataframe back to file."""
        file_name ="T_ONTIME_REPORTING"
        new_path = "/Users/lawhea1214/Documents/WGU/602/lorraine-w_task2/backup"
        date_version = f"{file_name}_{DataLoader.today}_{version}.{self.filetype}"
        new_name = os.path.join(new_path,date_version)
        try:
            if self.dataframe is None:
                raise ValueError("No dataframe loaded. Run load_data() first.")
            elif self.dataframe is not None: 
                self.dataframe.to_csv(new_name, index=False)
            else:
                raise ValueError("Unsupported file type. Use 'csv' or 'excel'.")
        except Exception as e:
            raise RuntimeError(f"Error saving data: {e}")
        


    
# test = DataLoader("/Users/lawhea1214/Documents/WGU/602/lorraine-w_task2/data", "T_ONTIME_REPORTING.csv")
# dft = test.load_data()
# test.save_versions(dft, "v1")