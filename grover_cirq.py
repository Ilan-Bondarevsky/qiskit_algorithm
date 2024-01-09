from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister, ClassicalRegister
#from quantum_circuits import cnz 
import math

from bit_functions import get_qubit_list

from abc import ABC, abstractmethod

from circuits import cnz, set_value_circuit


class grover_circuit(ABC):
    def oracle(self, nqubits, mode = 'noancilla', set_change_value=[]):
        '''Building an oracle giving the value of the qubits to go into the oracle.\n
        Each element of the list is a tuple with the index of the qubit and its value = (index, value)'''
        cnz_qc = cnz(nqubits, mode=mode)
        value_qc = set_value_circuit(nqubits, set_change_value, rest_hadamard=False)

        qc = QuantumCircuit(cnz_qc.qubits)
        qc = qc.compose(value_qc, get_qubit_list(qc))
        qc = qc.compose(cnz_qc, get_qubit_list(cnz_qc.qubits))
        qc = qc.compose(value_qc, get_qubit_list(qc))
        qc.name = 'Oracle'

        return qc
    
    
    def diffuser(self, nqubits, mode='noancilla'):
        cnz_cirq = cnz(nqubits, mode)
        qc = QuantumCircuit(cnz_cirq.qubits)
        
        qc.h(get_qubit_list(qc))
        qc.x(get_qubit_list(qc))
        qc.barrier(qc.qubits)
        qc = qc.compose(cnz_cirq, cnz_cirq.qubits)
        qc.barrier(qc.qubits)
        qc.x(get_qubit_list(qc))
        qc.h(get_qubit_list(qc))
        qc.name = f'Diffuser {nqubits}Q'

        return qc
    
    def prep_qubits(self, nqubits, prep_value = []):
        '''Prepare the qubits value and returns the circuit and the size of the "world", the amount of hadamard gates on the qubits'''
        qc = set_value_circuit(nqubits, prep_value, rest_hadamard=True)
        #qc = QuantumCircuit(nqubits)

        #one_qubit = [index[0] for index in prep_value if index[1] and index[0] < nqubits]
        #qc.x(one_qubit) if len(one_qubit) else None

        #h_qubit = [index for index in range(nqubits) if index not in [i[0] for i in prep_value]]
        #qc.h(h_qubit) if len(h_qubit) else None

        #world_size = len(h_qubit)
        qc.name = 'Prep Qubit'
        return qc, dict(qc.count_ops())['h']
    
    def calculate_iterations(self, qubit_world, solutions = 1):
        size_N = pow(2, qubit_world)
        if solutions is not None and solutions:
            if size_N < solutions * 2:
                return None
            return [math.floor((math.pi * math.sqrt(size_N / solutions)) / 4)]
        return list(range(1, math.floor((math.pi * math.sqrt(size_N)) / 4) + 1))

    def create_grover_circuit_with_iteration(self, iteration_qc, solutions = 1, prep_value = [], block_diagram = True):
        qubits = get_qubit_list(iteration_qc)
        prep_qc, world_qubit_size = self.prep_qubits(len(qubits), prep_value=prep_value)

        iterations = self.calculate_iterations(world_qubit_size, solutions)
        if iterations is None:
            return None

        grover_experiments = []
        for i in iterations:
            qc = QuantumCircuit(iteration_qc.qubits)
            if block_diagram:
                qc.append(prep_qc, qubits)
                [qc.append(iteration_qc.copy(), qc.qubits) for _ in range(i)]
            else:
                qc = qc.compose(prep_qc, qubits)
                for _ in range(i):
                    qc.barrier(qc.qubits)
                    qc = qc.compose(iteration_qc.copy(), qc.qubits)
                
            grover_experiments.append(qc)    
            
        return grover_experiments
           
    def add_qubit_measurement(self, circuit):
        qc = circuit.copy()
        qubits = get_qubit_list(qc)

        qc.add_register(ClassicalRegister(len(qubits)))
        qc.measure(qubits, qc.clbits)
        return qc

    @abstractmethod
    def calculation_data_circuit(self, nqubits):
        pass
    
    @abstractmethod
    def create_iteration(self):
        pass

    @abstractmethod
    def build_grover_iteration_data(self):
        pass







"""
def diffuser(nqubits, mode='noancilla'):
    qc = QuantumCircuit(QuantumRegister(nqubits))
    
    qc.h(range(nqubits))

    qc_cnz = cnz(len(qc.qubits), set_qubit_value=[(i, 0) for i in range(len(qc.qubits))], mode=mode)

    #qc.x(list(range(nqubits)))

    #qc.barrier(range(nqubits))

    #cnz_qc = cnz(len(qc.qubits), mode)
    
    qc.add_register(qc_cnz.ancillas)
    qc = qc.compose(qc_cnz, qc.qubits)

    #qc.barrier(range(nqubits))

    #qc.x(list(range(nqubits)))
    qc.h(range(nqubits))

    qc.name = f"Diffuser : {nqubits} qubits"
    return qc

def prep_qubits_circuit(nqubits, set_qubit_value = []):
    '''Prepare the qubits with Hadamard gate OR set qubits with values based on their index and value.\n
    Returns the prepared circuit and the number of qubits that complete the size of the circuit "world"\n
    set_value_list contains a list of tuples that contains (qubit_index , 0 or 1)'''

    qc = QuantumCircuit(nqubits)

    h_qubit = [h for h in range(nqubits) if h not in [value[0] for value in set_qubit_value]]
    zero_qubit = [value[0] for value in set_qubit_value if value[1]]

    qc.x(zero_qubit) if len(zero_qubit) else None
    qc.h(h_qubit) if len(h_qubit) else None

    return qc, len(h_qubit)

def calculate_iteration(nqubits, num_solution = 1):
    size_N = pow(2, nqubits)
    if num_solution is None or num_solution == 0:
        num_solution = 1
    return math.floor((math.pi * math.sqrt(size_N / num_solution)) / 4)

def simulate_grover_qc_list(grover_qc_list, circuit_index = None, min_percent = 10, sum_percent = 70, shots = 1024, all_simulations = False):
    if circuit_index is not None:
        grover_qc_list = [grover_qc_list[circuit_index]]

    op = QuantumOperation()
    output_qc = []
    for qc in grover_qc_list:
        op.set_circuit(qc)
        result = op.run_circuit(shots = shots)
        percent_list = {key : (100 * val / shots) for key, val in result['count'].items() if (100 * val / shots) >= min_percent}

        if all_simulations or sum(percent_list.values()) >= sum_percent:
            output_qc.append((op.get_circuit(), result['count']))
    return output_qc

def check_solution_grover(solutions, nqubits_size = None, max_value = None):
    if solutions is None:
        return True
    if nqubits_size is not None:
        max_v = pow(2, nqubits_size)
    elif max_value is not None:
        max_v = pow(2, max_value.bit_length())
    else:
        return False
    if solutions * 2 >= max_v:
        return False
    return True

def generate_grover_circuits_with_iterations(iteration_query, prep_qubit_value = [], solutions = 1, block_diagram=False):
    qc_output = []  

    query_qubits_list = get_qubit_list(iteration_query)

    prep_qc, nqubit_world = prep_qubits_circuit(len(query_qubits_list), prep_qubit_value)

    max_query = calculate_iteration(nqubit_world, 1)

    index_query = calculate_iteration(nqubit_world, num_solution=solutions) - 1 if solutions is not None else None

    qc = QuantumCircuit(iteration_query.qubits)
    qc = qc.compose(prep_qc, query_qubits_list)

    for i in range(max_query):
        if block_diagram:
            qc.append(iteration_query, qc.qubits)
        else:
            qc.barrier(qc.qubits)
            qc = qc.compose(iteration_query, qc.qubits)
            qc.barrier(qc.qubits)
        cur_qc = qc.copy()
        cur_qc.name = f"Grover {i}"
        qc_output.append(cur_qc)

    return qc_output, index_query
    """