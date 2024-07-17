import os
import csv
import pandas as pd

class CSVWriter:
    def __init__(self, folder_path, file_name):
        self.folder_path = folder_path
        self.file_name = file_name
        self.file_path = os.path.join(self.folder_path, self.file_name)
        
        # Create the folder if it does not exist
        os.makedirs(self.folder_path, exist_ok=True)
    
    def save_data(self, data, ignore_attr_tranplie = ["backend", "original_qc", "transpiled_qc"]):
        """
        Save the data to a CSV file using pandas.
        
        :param data: List of tuples (saved_transpile_action_parameters, ResultData)
        """
        combined_data = []
        for transpile_params, result_data in data:
            combined_dict = {**transpile_params.to_dict(ignore_attr = ignore_attr_tranplie), **result_data.to_dict()}
            combined_data.append(combined_dict)
        
        # Convert list of dictionaries to a pandas DataFrame
        df = pd.DataFrame(combined_data)
        
        # Save DataFrame to CSV
        df.to_csv(self.file_path, index=False)
        print(f"Data saved to {self.file_path}")
