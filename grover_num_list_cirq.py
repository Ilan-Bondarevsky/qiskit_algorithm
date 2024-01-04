from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister
from bit_functions import full_bitfield, get_qubit_list
from grover_cirq import diffuser, check_solution_grover, generate_grover_circuits_with_iterations
from quantum_circuits import cnz
from quantum_operation import QuantumOperation

def num_oracle(winner_list, max_list_value, mode = 'noancilla', block_diagram=False):
    '''Create a circquit to reflect the qubits when the input is one of the winning numbers.\n
    The max qubits is based on the max value given\n
    Can return the CNZ circuit to be a gate block or show its full circuit using BLOCK_DIAGRAM'''
    qc = QuantumCircuit(QuantumRegister(max_list_value.bit_length(), 'oracle_q'))

    qubit_list = get_qubit_list(qc)

    for num in winner_list:
        if num > max_list_value:
            raise MemoryError("Winner value higher than max value!")
        
        bit_list = full_bitfield(num, len(qubit_list))[::-1]
        
        neg_bit = [(i, val) for i, val in enumerate(bit_list)]

        qc_cnz = cnz(len(qubit_list), set_qubit_value=neg_bit, mode=mode)
        qc_cnz.name = f"cnz value = {num}"
        qc.add_register(qc_cnz.ancillas)

        if block_diagram:
            qc.append(qc_cnz, qubit_list + list(qc_cnz.ancillas))
        else:
            qc.barrier(qc.qubits)
            qc = qc.compose(qc_cnz, qubit_list + list(qc_cnz.ancillas))   
            qc.barrier(qc.qubits)

    qc.name = f'Oracle_Num {winner_list}'
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

def num_list_query(data_list, max_data_value, winner_list, mode = 'noancilla', block_diagram=False):
    qc_data = create_list_data_cirq(data_list, max_data_value, block_diagram=block_diagram)
    qc_oracle = num_oracle(winner_list, max_data_value, mode=mode, block_diagram=block_diagram)
    qc_diffuser = diffuser(mode=mode, nqubits=len(qc_data.qubits) - len(qc_data.ancillas))

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
    if not check_solution_grover(solutions=solutions, max_value=len(data_list)):
        raise MemoryError("To many solutions for Grover to work!")
    qc_query = num_list_query(data_list, max_data_value, winner_list, mode, block_diagram)
        
    return generate_grover_circuits_with_iterations(qc_query,solutions=solutions, block_diagram=block_diagram)

def find_num_query(winner_list, nqubits, mode = 'noancilla', block_diagram = False):
    max_list_value = pow(2, nqubits) - 1
    oracle_qc = num_oracle(winner_list, max_list_value, mode, block_diagram)
    diffuser_qc = diffuser(nqubits, mode=mode)    

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

    iteration_qc.name = "Find_Num_Query"
    return iteration_qc

def find_num_grover(winner_list, nqubits, mode = 'noancilla', block_diagram=False):
    if not check_solution_grover(solutions=len(winner_list), nqubits_size=nqubits):
        raise MemoryError("To many solutions for Grover to work!")
    query_qc = find_num_query(winner_list, nqubits, mode=mode,  block_diagram=block_diagram)

    return generate_grover_circuits_with_iterations(query_qc,solutions=len(winner_list), block_diagram=block_diagram)

x, y = grover_num_list([0,2,4,3,2,0,5,1], 5, [1,4], 2)

print(x)
print(y)

op = QuantumOperation()
op.set_circuit(x[y])
x = op.run_circuit()
print(x)