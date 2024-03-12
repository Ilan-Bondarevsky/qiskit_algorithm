from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister
from bit_functions import full_bitfield, get_qubit_list

from grover_cirq import grover_circuit

class find_num(grover_circuit):
    def __init__(self):
        super().__init__()

    @staticmethod
    def num_oracle(nqubits: int, winner_num : int) -> QuantumCircuit:
        bit_list = full_bitfield(winner_num, nqubits)[::-1]
        if nqubits < len(bit_list):
            raise Exception("The number needs more qubits!")
        
        index_list = [(index, int(not val)) for index, val in enumerate(bit_list)]

        qc = grover_circuit.oracle(nqubits, set_change_value=index_list)
        qc.name = f"Num_Oracle ({winner_num})"
        return qc
    
    @staticmethod
    def series_num_oracle(nqubits : int, winner_list :list , block_diagram = True) -> QuantumCircuit:
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
    
    def calculation_logic(self) -> QuantumCircuit:
        pass

    def build_iteration(self, winner_num_list : list = [], circuit_nqubits : int = 0, block_diagram=True) -> None:
        '''
        Build the iteration for the Grover circuit for the winner list
        :param circuit_nqubits = The number of qubits in the circuits (Minimum the vnumber needed for max value in the winner list)
        '''
        if not len(winner_num_list):
            raise Exception("Winner list is empty!")
        max_winner_qubit_needed = len(full_bitfield(max(winner_num_list)))
        circuit_nqubits = max(max_winner_qubit_needed, circuit_nqubits)
        qc = find_num.series_num_oracle(circuit_nqubits, winner_num_list, block_diagram)
        
        qubits = get_qubit_list(qc)
        diffuser_qc = grover_circuit.diffuser(len(qubits))
        qc.add_register(diffuser_qc.ancillas)
        if block_diagram:
            qc.append(diffuser_qc, qubits + list(diffuser_qc.ancillas))
        else:
            qc.barrier(qc.qubits)
            qc = qc.compose(diffuser_qc, qubits + list(diffuser_qc.ancillas))
            qc.barrier(qc.qubits)

        qc.name = "Grover_Find_Num_Iteration"
        self.iteration_qc = qc


class find_num_list(grover_circuit):
    def __init__(self):
        super().__init__()

    def __index_data_cirq(self, index : int, value : int, index_nqubits : int, value_nqubits : int) -> QuantumCircuit:
        '''
        Build a circuit to check a specific index and its value\n
        For 0, It will use X gates and cx gates for every value
        '''
        #https://arxiv.org/pdf/1502.04943.pdf
        qc = QuantumCircuit(QuantumRegister(index_nqubits, 'index'), AncillaRegister(value_nqubits, 'value'))
        index_bit_field = full_bitfield(index, index_nqubits)[::-1]
        value_bit_field = full_bitfield(value, value_nqubits)[::-1]

        for i in [i for i, _ in enumerate(index_bit_field) if not index_bit_field[i]]:
            qc.x(i)
        
        for bit in [i for i, _ in enumerate(value_bit_field) if value_bit_field[i]]:
            qc.mcx(list(range(len(index_bit_field))), qc.ancillas[bit])

        for i in [i for i, _ in enumerate(index_bit_field) if not index_bit_field[i]]:
            qc.x(i)
        
        qc.name = f"[I = {index}, Val = {value}]"
        return qc 
    
    def calculation_logic(self, num_array : list = [], block_diagram : bool = True) -> None:
        '''
        Return a Calculation Circuit for the find_num_list Grover circuit.
        '''
        if num_array is None or not len(num_array):
            return
        
        data_qc = QuantumCircuit(
            QuantumRegister(len(full_bitfield(len(num_array) - 1)), 'index'),
            AncillaRegister(len(full_bitfield(max(num_array))), 'data')
        )
        value_qubit_length = len(data_qc.ancillas)
        index_qubit_length = len(get_qubit_list(data_qc))

        for index, data in enumerate(num_array):
            if block_diagram:
                data_qc.append(self.__index_data_cirq(index, data, index_qubit_length, value_qubit_length), data_qc.qubits)
            else:
                data_qc.barrier(data_qc.qubits)
                data_qc = data_qc.compose(self.__index_data_cirq(index, data, index_qubit_length, value_qubit_length), data_qc.qubits)
        data_qc.name = f"Data {num_array}"
        self.calculation_qc = data_qc

    def build_iteration(self, winner_list = [], num_array : list = [], block_diagram=True, default_value:int = 0):
        '''
        Build a iteration for the Find_Num_In_List Grover circuit
        : param default_value is the default number in winner list, can search for it ONLY when the list is the length of 2 powered by N 
        '''
        if not len(num_array):
            raise Exception(f"The number array is empty!")
        if not len(winner_list):
            raise Exception(f"The winner list is empty!")
        if default_value in winner_list and pow(2, (len(num_array) - 1).bit_length()) != len(num_array):
            raise Exception(f"The winner list has a value of {default_value} when the number list is not the size of 2 powered by an N")
        
        self.calculation_logic(num_array, block_diagram)
        
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

        qc.name = "Grover_Find_Num_List_Iteration"
        self.iteration_qc = qc

if __name__ == "__main__":
    x =  find_num()
    x.build_iteration([5], 4, block_diagram=True)
    x.create_grover(solutions=1,block_diagram=False)
    print(x.measure_qc[0].draw())