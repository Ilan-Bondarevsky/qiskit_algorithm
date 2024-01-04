from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister
from quantum_circuits import cnz 
import math

from bit_functions import get_qubit_list
from quantum_operation import QuantumOperation

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