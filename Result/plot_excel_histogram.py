import matplotlib.pyplot as plt
import pandas as pd

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

if __name__ == "__main__":
    file_path = r'C:\Users\User\Downloads\x\outputfile\grover_circuit_A_6_qubits.csv'
    
    # plot_backend_histogram(file_path, ['result_time_taken','transpiled_qc_depth'], bin_value=[0.01, 100])
    data = pd.read_csv(file_path)
    data.drop(data[data['optimization_level']==3].index, inplace=True)

    plot_histogram(data, "result_time_taken", bin_width=0.01, vertical_line=0.0048742, additional_name_text = "Grover 6Q Search 6")
    plot_histogram(data, "transpiled_qc_depth", bin_width=10, vertical_line=1934, additional_name_text = "Grover 6Q Search 6")