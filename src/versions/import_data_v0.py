import pandas as pd
import numpy as np
import os

class DataLoader:
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

    def save_data(self):
        """Save self.dataframe back to file."""
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