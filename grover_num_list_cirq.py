from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister
from bit_functions import full_bitfield, get_qubit_list
from grover_cirq import diffuser, calculate_iteration, prep_search_qubits, check_solution_grover, generate_grover_circuits_with_iterations
from quantum_circuits import cnz

def num_oracle(winner_list, max_list_value, mode = 'noancilla', block_diagram=False, worker_qubit=False):
    '''Create a circquit to reflect the qubits when the input is one of the winning numbers.\n
    The max qubits is based on the max value given\n
    Can return the CNZ circuit to be a gate block or shhow its full circuit using BLOCK_DIAGRAM'''
    worker_anc = AncillaRegister(int(worker_qubit), 'worker_anc')
    qc = QuantumCircuit(QuantumRegister(max_list_value.bit_length(), 'oracle_q'), worker_anc)

    qubit_list = get_qubit_list(qc)

    for index, num in enumerate(winner_list):
        if num > max_list_value:
            raise MemoryError("Winner value higher than max value!")
        
        qc.barrier(qc.qubits)
        bit_list = full_bitfield(num, len(qubit_list))[::-1]
        
        neg_bit = [i for i,_ in enumerate(bit_list) if not bit_list[i]]
        qc.x(neg_bit) if len(neg_bit) else None
        if worker_qubit:
            qc.mcx(qubit_list, worker_anc)
        else:
            qc_cnz = cnz(len(qubit_list), mode)
            cnz_anc = AncillaRegister(len(qc_cnz.ancillas), f"cnz_anc_{index}")
            qc.add_register(cnz_anc)
            if block_diagram:
                qc.append(qc_cnz, qubit_list + list(cnz_anc))
            else:
                qc.barrier(qc.qubits)
                qc = qc.compose(qc_cnz, qubit_list + list(cnz_anc))   
                qc.barrier(qc.qubits)
    
        qc.x(neg_bit) if len(neg_bit) else None
        qc.barrier(qc.qubits)

    qc.name = 'Oracle_Num ' + str(winner_list)
    return qc

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

    prep_qc, size_n = prep_search_qubits(len(query_qubits))

    index_query = None if solutions is None else calculate_iteration(size_n, solutions) - 1

    qc_output = generate_grover_circuits_with_iterations(prep_qc, qc_query, block_diagram)
        
    return qc_output, index_query

def simple_search_grover(winner_list, nqubits, mode = 'noancilla', block_diagram=False, worker_qubit=False):
    max_list_value = pow(2, nqubits) - 1

    if not check_solution_grover(solutions=len(winner_list), max_value=max_list_value):
        raise MemoryError("To many solutions for Grover to work!")

    oracle_qc = num_oracle(winner_list, max_list_value, mode, block_diagram, worker_qubit)
    diffuser_qc = diffuser(nqubits, mode=mode, worker_qubit=False)

    iteration_qc = QuantumCircuit(oracle_qc.qubits, diffuser_qc.ancillas)
    cur_qubits = get_qubit_list(iteration_qc)
    if block_diagram:
        iteration_qc.append(oracle_qc.copy(), cur_qubits + list(oracle_qc.ancillas))
        iteration_qc.append(diffuser_qc.copy(), cur_qubits + list(diffuser_qc.ancillas))
    else:
        iteration_qc.barrier(iteration_qc.qubits)
        iteration_qc = iteration_qc.compose(oracle_qc.copy(), cur_qubits + list(oracle_qc.ancillas))
        iteration_qc.barrier(iteration_qc.qubits)
        iteration_qc = iteration_qc.compose(diffuser_qc.copy(), cur_qubits + list(diffuser_qc.ancillas))
        iteration_qc.barrier(iteration_qc.qubits)

    qc = QuantumCircuit(iteration_qc.qubits)
    cur_qubits = get_qubit_list(qc)

    prep_qc, size_n = prep_search_qubits(nqubits)

    qc = qc.compose(prep_qc, cur_qubits)

    queries = calculate_iteration(size_n, len(winner_list))

    for i in range(queries):
        cur_iteration = iteration_qc.copy()
        cur_iteration.name = f"Iteration {i}"
        if block_diagram:
            qc.append(cur_iteration, qc.qubits)
        else:
            qc.barrier(qc.qubits)
            qc = qc.compose(cur_iteration, qc.qubits)
            qc.barrier(qc.qubits)
    qc.name = "Grover Algo"
    return qc