import pandas as pd
import numpy as np
import os
import sys



class OriginalData():
    def __init__(self, url, filename, filetype='csv'):
        self.url = url
        self.filename = filename
        self.filetype = filetype
        self.filepath = os.path.join(url, filename)
        self.dataframe = None

    def load_data(self):
        """Load dataset into a DataFrame."""
        try:
            if self.filetype == 'csv':
                self.dataframe = pd.read_csv(self.filepath)
            elif self.filetype == 'excel':
                self.dataframe = pd.read_excel(self.filepath)
            else:
                raise ValueError("Unsupported file type. Use 'csv' or 'excel'.")
        except Exception as e:
            raise RuntimeError(f"Error loading data: {e}")
        return self.dataframe
        
    # def subset(self, dataframe, columns):
    #     subset_ls = []
    #     for x in columns:
    #         subset_ls.append(x)

    #     """Filter the DataFrame to include only specific columns."""
    #     self.dataframe.loc[:, subset_ls]


    #     return self.dataframe

loader = OriginalData("/Users/lawhea1214/Documents/WGU/602/lorraine-w_task2/backup", "T_ONTIME_REPORTING.csv")
test = loader.load_data()
print(test.head())