from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister, transpile
from bit_functions import full_bitfield, get_qubit_list
from grover_cirq import diffuser, check_solution_grover, generate_grover_circuits_with_iterations
from circuits import cnz

from grover_cirq import grover_circuit

from qiskit import Aer, execute

class find_num(grover_circuit):
    def calculation_data_circuit(self, nqubits, winner):
        if winner is None:
            return None
        if not isinstance(winner, int):
            return None
        
        qc = QuantumCircuit(nqubits)
        bit_list = full_bitfield(winner, nqubits)[::-1]
        
        zero_value = [i for i, val in enumerate(bit_list) if not val]
        qc.x(zero_value) if len(zero_value) else None
        
        qc.name = f'Find {winner}'
        return qc
    
    def create_iteration(self, nqubits, winner_list = [], block_diagram =True):
        diffuser_qc = self.diffuser(nqubits)
        
        qc_output = QuantumCircuit(nqubits)
        qubits = qc_output.qubits

        for winner in set(winner_list):
            win_qc = self.calculation_data_circuit(nqubits=nqubits, winner=winner)
            oracle_qc = self.oracle(nqubits, [])
            if block_diagram:
                qc_output.append(win_qc, qubits)

                oracle_qc = self.oracle(nqubits)
                qc_output.add_register(oracle_qc.ancillas)
                qc_output.append(oracle_qc, list(qubits) + list(oracle_qc.ancillas))

                qc_output.append(win_qc.inverse(), qubits)
            else:
                qc_output = qc_output.compose(win_qc, qubits)
                qc_output.barrier(qc_output.qubits)

                oracle_qc = self.oracle(nqubits)
                qc_output.add_register(oracle_qc.ancillas)
                qc_output = qc_output.compose(oracle_qc, list(qubits) + list(oracle_qc.ancillas))

                qc_output.barrier(qc_output.qubits)
                qc_output = qc_output.compose(win_qc.inverse(), qubits)
                qc_output.barrier(qc_output.qubits)


        qc_output.add_register(diffuser_qc.ancillas)
        if block_diagram:
            qc_output.append(diffuser_qc, list(qubits) + list(diffuser_qc.ancillas))
        else:
            qc_output = qc_output.compose(diffuser_qc, list(qubits) + list(diffuser_qc.ancillas))
            qc_output.barrier(qc_output.qubits)
        qc_output.name = f"Query"
        return qc_output

    def create_grover(self, nqubits, winner_list):
        iter_qc = self.create_iteration(nqubits, winner_list=winner_list)
        return self.create_grover_circuit_with_iter(iter_qc, solutions = len(winner_list))
        

class search_index_list(grover_circuit):
    def calculation_data_circuit(self, data_array = [], block_diagram=True):
        data_qc = QuantumCircuit(
            QuantumRegister(len(full_bitfield(len(data_array) - 1)), 'index'),
            AncillaRegister(len(full_bitfield(max(data_array))), 'data')
        )
        value_length = len(data_qc.ancillas)
        index_length = len(get_qubit_list(data_qc))
        for i, val in enumerate(data_array):
            cur_index = self.index_data_cirq(i, val, index_length, value_length)
            if block_diagram:
                data_qc.append(cur_index, data_qc.qubits)
            else:
                data_qc = data_qc.compose(cur_index, data_qc.qubits)
        data_qc.name = f"Data Array: {data_array}"
        return data_qc
        
    def create_iteration(self, data_array = [], winner_list = [], block_diagram = True):
        data_qc = self.calculation_data_circuit(data_array=data_array, block_diagram=block_diagram)

        qc_output = QuantumCircuit(data_qc.qubits)
        qubit_list = get_qubit_list(qc_output)
        value_list = list(data_qc.ancillas)
        if block_diagram:
            qc_output.append(data_qc, data_qc.qubits)
        else:
            qc_output = qc_output.compose(data_qc, data_qc.qubits)

        for winner in set(winner_list):
            x_index = self.get_qubit_index_of_zeros(nqubits=len(value_list), num= winner)
            [qc_output.x(value_list[index]) for index in x_index]
            
            oracle_qc = self.oracle(len(value_list))
            qc_output.add_register(oracle_qc.ancillas)
            if block_diagram:
                qc_output.append(oracle_qc, value_list + list(oracle_qc.ancillas))
            else:
                qc_output.barrier(qc_output.qubits)
                qc_output = qc_output.compose(oracle_qc, value_list + list(oracle_qc.ancillas))
                qc_output.barrier(qc_output.qubits)
            [qc_output.x(value_list[index]) for index in x_index]

        if block_diagram:
            qc_output.append(data_qc.inverse(), data_qc.qubits)
        else:
            qc_output = qc_output.compose(data_qc.inverse(), data_qc.qubits)
            qc_output.barrier(qc_output.qubits)

        diffuser_qc = self.diffuser(len(qubit_list))
        qc_output.add_register(diffuser_qc.ancillas)
        if block_diagram:
            qc_output.append(diffuser_qc, qubit_list + list(diffuser_qc.ancillas))
        else:
            qc_output = qc_output.compose(diffuser_qc, qubit_list + list(diffuser_qc.ancillas))
            qc_output.barrier(qc_output.qubits)
        qc_output.name = f"Query"

        return qc_output

    def build_grover_iteration_data(self, data_array, winner_list, num_solution = None, block_diagram=True):
        iter_qc = self.create_iteration(data_array=data_array, winner_list = winner_list, block_diagram=block_diagram)
        return self.create_grover_circuit_with_iter(iter_qc, solutions = num_solution, block_diagram=block_diagram)

    def index_data_cirq(self, index, value, index_qubits, value_qubits):
        #https://arxiv.org/pdf/1502.04943.pdf
        qc = QuantumCircuit(QuantumRegister(index_qubits, 'index'), AncillaRegister(value_qubits, 'value'))
        index_bit_field = full_bitfield(index, index_qubits)[::-1]
        value_bit_field = full_bitfield(value, value_qubits)[::-1]

        for i in [i for i, _ in enumerate(index_bit_field) if not index_bit_field[i]]:
            qc.x(i)
        
        for bit in [i for i, _ in enumerate(value_bit_field) if value_bit_field[i]]:
            qc.mcx(list(range(len(index_bit_field))), qc.ancillas[bit])

        for i in [i for i, _ in enumerate(index_bit_field) if not index_bit_field[i]]:
            qc.x(i)
        
        qc.name = f"[I = {index}, Val = {value}]"
        return qc 
    
    def get_qubit_index_of_zeros(self, nqubits, num):
        bit_list = full_bitfield(num, nqubits)[::-1]
        
        zero_value = [i for i, val in enumerate(bit_list) if not val]
        return zero_value
    


x = full_bitfield(2, 5)[::-1]
print(x)
y = [not i for i in x]
print(y)