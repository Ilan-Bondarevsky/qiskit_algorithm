import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_histogram(data, field, *, bin_width, min_value=None, max_value=None, vertical_line=None, additional_name_text : str = ''):
    time_taken = data[field]
    
    if min_value is not None:
        filtered_data = time_taken[time_taken >= min_value]
    if max_value is not None:
        filtered_data = filtered_data[filtered_data <= max_value] if min_value is not None else time_taken[time_taken <= max_value]
    else:
        filtered_data = time_taken

    plt.figure(figsize=(10, 6))
    if vertical_line is not None:
        plt.axvline(vertical_line, color='red', linestyle='--', linewidth=2, label=f'Aer {field}: {vertical_line}')
    plt.hist(filtered_data, bins=int((filtered_data.max() - filtered_data.min()) / bin_width), edgecolor='black')
    plt.title(f'{additional_name_text} Histogram of {field}')
    plt.xlabel(field)
    plt.ylabel('Counts')
    plt.grid(True)
    if vertical_line is not None:
        plt.legend()
    plt.show()

def plot_backend_histogram(file_path, field_list : list[str], backend_compare : str = 'aer_simulator', optimization_level_drop : int = 3, bin_value : list[float] | None = None, additional_name_text : str = ''):
    data = pd.read_csv(file_path)
    data.drop(data[data['optimization_level']==optimization_level_drop].index, inplace=True)
    if not isinstance(field_list, list):
        field_list = [field_list]
    compare_row = data[data['backend_name'] == backend_compare]
    data.drop(data[data['backend_name']==backend_compare].index, inplace=True)
    if bin_value is not None and len(bin_value) != len(field_list):
        bin_value = None
    for index, field in enumerate(field_list):
        vertical_line = compare_row[field].values[0]
        bin_width = round(data[field].min(), 2) if bin_value is None else bin_value[index]
        plot_histogram(data, field, bin_width=bin_width, vertical_line=vertical_line, additional_name_text = additional_name_text)

def combine_csv_files_in_folder(folder_path : str, file_name : str = "combined_file.csv"):
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    data_frames = [pd.read_csv(os.path.join(folder_path, file)) for file in csv_files]
    combined_df = pd.concat(data_frames, ignore_index=True)
    file_path = os.path.join(folder_path, file_name)
    combined_df.to_csv(file_path, index=False)
    return file_path
    
if __name__ == "__main__":
    # combine_csv_files_in_folder(r"C:\Users\User\Desktop\code\qiskit_algorithm\logs\Grover_Data_list")
    file_path = r'C:\Users\User\Desktop\code\qiskit_algorithm\logs\Grover_Data_list\combined_file.csv'
    
    # plot_backend_histogram(file_path, ['result_time_taken','transpiled_qc_depth'], bin_value=[0.01, 100])
    data = pd.read_csv(file_path)
    data.drop(data[data['optimization_level']==3].index, inplace=True)
    data.drop(data[data['backend_name']=='aer_simulator'].index, inplace=True)

    plot_histogram(data, "result_time_taken", bin_width=0.01, vertical_line=0.027247, additional_name_text = "Grover Search 4's Index in list [3, 10, 7, 6, 2, 8, 14, 1, 5, 9, 11, 4, 13, 0, 15, 12]")
    plot_histogram(data, "transpiled_qc_depth", bin_width=10, vertical_line=14387, additional_name_text = "Grover Search 4's Index in list [3, 10, 7, 6, 2, 8, 14, 1, 5, 9, 11, 4, 13, 0, 15, 12]")