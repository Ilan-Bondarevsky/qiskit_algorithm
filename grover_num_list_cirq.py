from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister
from bit_functions import full_bitfield, get_qubit_list
from quantum_circuits import cnz, z_or
from grover_cirq import diffuser, calculate_iteration, h_prep, simulate_grover_qc_list, check_solution_grover
from grover_oracle import num_oracle
import math
from quantum_operation import QuantumOperation
from qiskit.tools.visualization import plot_histogram
#https://arxiv.org/pdf/1502.04943.pdf
def index_data_cirq(index, value, index_qubits, value_qubits):
    '''Create a circuit that create a connection between an index and a value in a circuit\n
    Each index has a specific value.'''
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

def create_list_data_cirq(data_list, max_value_in_list, block_diagram=False):
    qc = QuantumCircuit(
        QuantumRegister(len(full_bitfield(len(data_list) - 1)), 'index'),
        AncillaRegister(len(full_bitfield(max_value_in_list)), 'data')
    )
    
    for i, val in enumerate(data_list):
        cur_index = index_data_cirq(i, val, len(qc.qubits) - len(qc.ancillas), len(qc.ancillas))
        if block_diagram:
            qc.append(cur_index, qc.qubits)
        else:
            qc.barrier(qc.qubits)
            qc = qc.compose(cur_index, qc.qubits)   
            qc.barrier(qc.qubits)
    qc.name = f"Data_list {data_list} with max value of {max_value_in_list}"
    return qc

def num_list_query(data_list, max_data_value, winner_list, mode = 'noancilla', block_diagram=False, worker_qubit=False):
    qc_data = create_list_data_cirq(data_list, max_data_value, block_diagram=block_diagram)
    qc_oracle = num_oracle(winner_list, max_data_value, mode=mode, block_diagram=block_diagram, worker_qubit=worker_qubit)
    qc_diffuser = diffuser(mode=mode, nqubits=len(qc_data.qubits) - len(qc_data.ancillas), worker_qubit=worker_qubit)

    qc = QuantumCircuit(qc_data.qubits, qc_oracle.ancillas, qc_diffuser.ancillas)
    if block_diagram:
        qc.append(qc_data, qc_data.qubits)
        qc.append(qc_oracle, qc_data.ancillas)
        qc.append(qc_data.inverse(), qc_data.qubits)
        qc.append(qc_diffuser, get_qubit_list(qc) + list(qc_diffuser.ancillas))
    else:
        qc.barrier(qc.qubits)
        qc = qc.compose(qc_data, qc_data.qubits)   
        qc.barrier(qc.qubits)
        qc = qc.compose(qc_oracle, qc_data.ancillas)  
        qc.barrier(qc.qubits)
        qc = qc.compose(qc_data.inverse(), qc_data.qubits) 
        qc.barrier(qc.qubits)
        qc = qc.compose(qc_diffuser, get_qubit_list(qc) + list(qc_diffuser.ancillas))
        qc.barrier(qc.qubits)
    qc.name = 'Num_List_Query'
    return qc

def grover_num_list(data_list, max_data_value, winner_list, solutions=None, mode='noancilla', block_diagram=False):    
    qc_query = num_list_query(data_list, max_data_value, winner_list, mode, block_diagram)
    query_qubits = get_qubit_list(qc_query)

    if not check_solution_grover(solutions=solutions, max_value=len(data_list)):
        raise MemoryError("To many solutions for Grover to work!")

    max_query = calculate_iteration(len(query_qubits), 1)
    index_query = None if solutions is None else calculate_iteration(len(query_qubits), solutions) - 1


    prep_qc = h_prep(len(query_qubits))

    qc_output = []

    qc = QuantumCircuit(qc_query.qubits)
    qc = qc.compose(prep_qc, query_qubits)
    for i in range(max_query):
        if block_diagram:
            qc.append(qc_query, qc.qubits)
        else:
            qc.barrier(qc.qubits)
            qc = qc.compose(qc_query, qc.qubits)
            qc.barrier(qc.qubits)
        cur_qc = qc.copy()
        cur_qc.name = f"Grover {i}"
        qc_output.append(cur_qc)
        
    return qc_output, index_query