import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime
from step_b_import_data import DataLoader
from step_b_format_data import CleanData
from dateutil import parser

class filterColumns(DataLoader):
    def __init__(self, url, filename, filetype='csv'):
        super().__init__(url, filename, filetype)
        self.dataframe = self.load_data()

    def filter(self, column, data):
        """Filter the dataframe for specific airports."""
        self.dataframe = self.dataframe[self.dataframe[column].str.upper() == data.upper()]
        return self.dataframe
    
    def time_convert(self, col_lst):
        counter = 0
        shape = self.dataframe.shape[0] + 1
        while counter <= shape:
            for col in col_lst:
                time_parser = parser.parse(self.dataframe.loc[counter, col])
                time = time_parser.time()
                self.dataframe[col] = self.dataframe[col].apply(lambda x: time.hour * 1000 + time.minute*100 + time.second)
            return self.dataframe
        
    def remove_outliers(self):
        for col in self.dataframe.columns:
            cmean = self.dataframe[col].mean()
            q1 = self.dataframe[col].quantile(0.25)
            q3 = self.dataframe[col].quantile(0.75)
            iqr = q3 - q1
            highOutliers = q3 + (iqr*1.5)
            lowOutliers = q1 + (iqr*1.5)
            self.dataframe[col] = self.dataframe[col].apply(lambda x: cmean if x  < lowOutliers or x > highOutliers else x)

    


# loader = filterColumns("/Users/lawhea1214/Documents/WGU/602/lorraine-w_task2/backup", "T_ONTIME_REPORTING.csv")
# col_lst = ["FL_DATE"]
# test = loader.load_data()
# test = loader.time_convert(col_lst)
# print(test)
