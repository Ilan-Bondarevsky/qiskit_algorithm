import os
import csv
import pandas as pd

import sys
# current_dir = os.getcwd()
# sys.path.append(os.path.dirname(os.path.abspath(current_dir)))
from datetime import datetime

class CSVWriter:
    def __init__(self, file_name : str, folder_path : str = "..\logs"):
        self.folder_path = folder_path
        split_name = file_name.split('.')
        if len(split_name) > 2:
            raise Exception("There are dots '.' in the file name, only one before the type")
        self.file_name = split_name[0]
        if len(split_name) > 1:
            self.file_type = split_name[1]
        else:
            self.file_type = 'csv'
        
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("_%Y_%m_%d_%H_%M_%S")
        
        self.full_file_name = ''.join([self.file_name, formatted_datetime, '.', self.file_type])
        
        self.file_path = os.path.join(self.folder_path, self.full_file_name)
        # Create the folder if it does not exist
        os.makedirs(self.folder_path, exist_ok=True)
    
    def save_data(self, data, ignore_attr_tranplie = ["backend", "original_qc", "transpiled_qc"]):
        """
        Save the data to a CSV file using pandas.
        
        :param data: List of tuples (saved_transpile_action_parameters, ResultData)
        """
        combined_data = []
        # Transform data to dictionary
        for transpile_params, result_data in data:
            combined_dict = {**transpile_params.to_dict(ignore_attr = ignore_attr_tranplie), **result_data.to_dict()}
            combined_data.append(combined_dict)
        # Get keys of data
        keys = set([])
        for data_dict in combined_data:
            keys.update(list(data_dict.keys()))
        # Add missing keys to dict with empty value
        for data_dict in combined_data:
            for key in keys:
                if key not in set(list(data_dict.keys())):
                    data_dict[key] = ''
        
        # Convert list of dictionaries to a pandas DataFrame
        df = pd.DataFrame(combined_data)
        
        # Save DataFrame to CSV
        df.to_csv(self.file_path, index=False)
        print(f"Data saved to {self.file_path}")

if __name__ == "__main__":
    write = CSVWriter("try")
    print(write.file_path)
    write.save_data(data=[])