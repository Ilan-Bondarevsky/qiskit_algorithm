from data_list_grover import DataListGrover
from quantum_cirq_func import create_h_prep
data_list = [1,2,3,4]
winner = 2
list_grover = DataListGrover(data_list, winner, prep_func=create_h_prep)
list_grover.create_data()
#list_grover.create_oracle(nqubits=None)
list_grover.create_oracle(nqubits=list_grover.circuit['data'].num_ancillas)
list_grover.create_iteration()
list_grover.create_full_grover(answers=1)

list_grover.run_circuit('full')
list_grover.draw_histogram(file_directory=None)
y = list_grover.get_circuits()
list_grover.draw_circuit('full', 'mpl')