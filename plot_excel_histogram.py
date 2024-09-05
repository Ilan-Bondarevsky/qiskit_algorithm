import matplotlib.pyplot as plt
import pandas as pd

def plot_histogram(data, field, *, bin_width, min_value=None, max_value=None, vertical_line=None):
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
    plt.title('Histogram of Result Time Taken')
    plt.xlabel('Result Time Taken')
    plt.ylabel('Frequency')
    plt.grid(True)
    if vertical_line is not None:
        plt.legend()
    plt.show()

file_path = r'D:\myProjects\AfekaCodeProjects\codeProjects\FinalProject_qiskit\qiskit_algorithm\logs\add_mod_11_results_2000_plus_48_2024_08_20_18_18_10.csv'
data = pd.read_csv(file_path)
data.drop(data[data['optimization_level']==3].index, inplace=True)

plot_histogram(data, "result_time_taken", bin_width=10, max_value=1000, vertical_line=0.011923)
plot_histogram(data, "transpiled_qc_depth", bin_width=10, vertical_line=175)