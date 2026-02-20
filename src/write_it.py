import pandas as pd
from step_b_import_data import DataLoader, FileLoader



class WriteIt(FileLoader):
    def __init__(self, url, filename, filetype=None):
        super().__init__(url, filename, filetype)
        pass