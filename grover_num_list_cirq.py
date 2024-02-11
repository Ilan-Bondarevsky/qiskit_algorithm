from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister
from bit_functions import full_bitfield, get_qubit_list

from grover_cirq import grover_circuit

class find_num(grover_circuit):
    def __init__(self):
        super().__init__()

    @staticmethod
    def num_oracle(nqubits, winner_num):
        if not isinstance(winner_num, int):
            raise Exception("The winner number has to be a number!")
        
        bit_list = full_bitfield(winner_num, nqubits)[::-1]
        if nqubits < len(bit_list):
            raise Exception("The number needs more qubits!")
        
        index_list = [(index, int(not val)) for index, val in enumerate(bit_list)]

        qc = grover_circuit.oracle(nqubits, set_change_value=index_list)
        qc.name = f"Num_Oracle ({winner_num})"
        return qc      

    @staticmethod
    def series_num_oracle(nqubits, winner_list, block_diagram = True):
        qc = QuantumCircuit(nqubits)
        for num in winner_list:
            cur_qc = find_num.num_oracle(nqubits, num)
            if block_diagram:
                qc.append(cur_qc, qc.qubits)
            else:
                qc.barrier(qc.qubits)
                qc = qc.compose(cur_qc, qc.qubits)
                qc.barrier(qc.qubits)
        qc.name = f"Oracle {list(winner_list)}"
        return qc

    def __index_data_cirq(self, index, value, index_qubits, value_qubits):
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
    
    def calculation_logic(self, data_array = [], block_diagram = True):
        if data_array is None or not len(data_array):
            return
        
        data_qc = QuantumCircuit(
            QuantumRegister(len(full_bitfield(len(data_array) - 1)), 'index'),
            AncillaRegister(len(full_bitfield(max(data_array))), 'data')
        )
        value_qubit_length = len(data_qc.ancillas)
        index_qubit_length = len(get_qubit_list(data_qc))

        for index, data in enumerate(data_array):
            if block_diagram:
                data_qc.append(self.__index_data_cirq(index, data, index_qubit_length, value_qubit_length), data_qc.qubits)
            else:
                data_qc.barrier(data_qc.qubits)
                data_qc = data_qc.compose(self.__index_data_cirq(index, data, index_qubit_length, value_qubit_length), data_qc.qubits)
        data_qc.name = f"Data {data_array}"
        self.calculation_qc = data_qc

    def build_iteration(self, winner_list = [], data=None, block_diagram=True):
        '''Build the iteration of the grover circuit.\n
        Data is a list of Integers to search the winner from the list.\n
        Data is None to create a circuit the size of the winner bit value.\n
        Data is an Integer to create a circuit in the size of DATA qubits.'''
        max_qubit = 0
        if isinstance(data, int):
            max_qubit = data
            data = []
        else:
            self.calculation_logic(data, block_diagram)
        
        if self.calculation_qc is None:
            qc = find_num.series_num_oracle(max(len(full_bitfield(max(winner_list))), max_qubit), winner_list, block_diagram)
        else:
            qc = QuantumCircuit(self.calculation_qc.qubits)
            if block_diagram:
                qc.append(self.calculation_qc, qc.qubits)
                oracle = find_num.series_num_oracle(len(qc.ancillas), winner_list, block_diagram)
                qc.append(oracle, qc.ancillas)
                qc.append(self.calculation_qc.inverse(), qc.qubits)
            else:
                qc = qc.compose(self.calculation_qc, qc.qubits)
                qc.barrier(qc.qubits)
                oracle = find_num.series_num_oracle(len(qc.ancillas), winner_list, block_diagram)
                qc = qc.compose(oracle, qc.ancillas)
                qc.barrier(qc.qubits)
                qc = qc.compose(self.calculation_qc.inverse(), qc.qubits)
        
        qubits = get_qubit_list(qc)
        diffuser_qc = grover_circuit.diffuser(len(qubits))
        qc.add_register(diffuser_qc.ancillas)
        if block_diagram:
            qc.append(diffuser_qc, qubits + list(diffuser_qc.ancillas))
        else:
            qc.barrier(qc.qubits)
            qc = qc.compose(diffuser_qc, qubits + list(diffuser_qc.ancillas))
            qc.barrier(qc.qubits)

        qc.name = "Grover_Iteration"
        self.iteration_qc = qc