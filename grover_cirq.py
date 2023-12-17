from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister
from quantum_circuits import cnz 
import math

from grover_oracle import num_oracle
from bit_functions import get_qubit_list
from quantum_operation import QuantumOperation

def diffuser(nqubits, mode='noancilla', worker_qubit=False):
    qc = QuantumCircuit(QuantumRegister(nqubits), AncillaRegister(int(worker_qubit)))
    
    qc.h(range(nqubits))
    qc.x(list(range(nqubits)))

    qc.barrier(range(nqubits))
    if worker_qubit:
        qc.mcx(list(range(nqubits)), qc.ancillas)
    else:
        cnz_qc = cnz(len(qc.qubits), mode)
        qc.add_register(cnz_qc.ancillas)
        qc = qc.compose(cnz_qc, get_qubit_list(qc) + list(cnz_qc.ancillas))
    qc.barrier(range(nqubits))

    qc.x(list(range(nqubits)))
    qc.h(range(nqubits))

    qc.name = f"Diffuser : {nqubits} qubits"
    return qc

def h_prep(nqubits):
    qc = QuantumCircuit(nqubits)
    qc.h(qc.qubits)
    return qc

def calculate_iteration(nqubits, num_solution = 1):
    size_N = pow(2, nqubits)
    if num_solution is None:
        num_solution = 1
    return math.floor((math.pi * math.sqrt(size_N / num_solution)) / 4)

def simple_search_grover(winner_list, nqubits, mode = 'noancilla', block_diagram=False, worker_qubit=False):
    max_list_value = pow(2, nqubits) - 1

    if not check_solution_grover(solutions=len(winner_list), max_value=max_list_value):
        raise MemoryError("To many solutions for Grover to work!")

    oracle_qc = num_oracle(winner_list, max_list_value, mode, block_diagram, worker_qubit)

    qc = QuantumCircuit(oracle_qc.qubits)
    cur_qubits = get_qubit_list(qc)
    qc = qc.compose(h_prep(nqubits), cur_qubits)
    
    diffuser_qc = diffuser(nqubits, mode=mode, worker_qubit=False)
    qc.add_register(diffuser_qc.ancillas)

    queries = calculate_iteration(nqubits, len(winner_list))
    print(queries)
    for _ in range(queries):
        if block_diagram:
            qc.append(oracle_qc.copy(), cur_qubits + list(oracle_qc.ancillas))
            qc.append(diffuser_qc.copy(), cur_qubits + list(diffuser_qc.ancillas))
        else:
            qc.barrier(qc.qubits)
            qc = qc.compose(oracle_qc.copy(), cur_qubits + list(oracle_qc.ancillas))
            qc.barrier(qc.qubits)
            qc = qc.compose(diffuser_qc.copy(), cur_qubits + list(diffuser_qc.ancillas))
            qc.barrier(qc.qubits)
    qc.name = "Grover Algo"
    return qc

def simulate_grover_qc_list(grover_qc_list, min_percent = 10, sum_percent = 70, shots = 1024, circuit_index = None, all_simulations = False):
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
    max_v = 0
    if nqubits_size is not None:
        max_v = pow(2, nqubits_size)
    elif max_value is not None:
        max_v = pow(2, max_value.bit_length())
    else:
        return False
    if solutions * 2 >= max_v:
        return False
    return True