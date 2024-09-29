import sys
sys.path.insert(0, "D:/myProjects/AfekaCodeProjects/codeProjects/FinalProject_qiskit/qiskit_algorithm")

import pandas as pd

from Result.plot_excel_histogram import plot_histogram


file_path = r"D:\myProjects\AfekaCodeProjects\codeProjects\FinalProject_qiskit\qiskit_algorithm\logs\add_mod_11_results_2000_plus_48_2024_08_20_18_18_10.csv"
# file_path = r"D:\myProjects\AfekaCodeProjects\codeProjects\FinalProject_qiskit\qiskit_algorithm\logs\add_2000_plus_48_backends_2024_09_07_14_22_03.csv"

data = pd.read_csv(file_path)
data.drop(data[data['optimization_level']==3].index, inplace=True)

plot_histogram(data, "result_time_taken", bin_width=10, vertical_line=0.011923, max_value=1000, additional_name_text = "Draper add 2000+48")
plot_histogram(data, "transpiled_qc_depth", bin_width=10, vertical_line=100, additional_name_text = "Draper add 2000+48")


