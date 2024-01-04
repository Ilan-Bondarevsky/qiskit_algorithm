from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister, ClassicalRegister, Aer, execute
from bit_functions import full_bitfield, get_qubit_list
from grover_cirq import diffuser, calculate_iteration, prep_qubits_circuit, check_solution_grover, generate_grover_circuits_with_iterations, simulate_grover_qc_list
from quantum_circuits import cnz
from quantum_logic_gates import and_gate, or_gate, xor_gate, xnor_gate, nand_gate, nor_gate, mor_gate, mand_gate
from grover_cirq import diffuser
from quantum_operation import QuantumOperation

def check_same_num(num_qubit = None, max_num_value = None):
    '''Returns a circuit that sets the last ancilla qubit (Answer) if the numbers are the same'''
    if num_qubit is None and max_num_value is None:
        return None
    if num_qubit is not None:
        pass
    else:
        num_qubit = max_num_value.bit_length()

    num_a = QuantumRegister(num_qubit, 'A')
    num_b = QuantumRegister(num_qubit, 'B')
    xnor_qc = QuantumCircuit(num_a, num_b)

    for i in range(num_qubit):
        xnor_g = xnor_gate()
        xnor_qc.add_register(AncillaRegister(1))
        xnor_qc = xnor_qc.compose(xnor_g, [num_a[i], num_b[i], xnor_qc.ancillas[-1]])
    
    qc = QuantumCircuit(xnor_qc.qubits)
    qc = qc.compose(xnor_qc, xnor_qc.qubits)
    if len(qc.ancillas) > 1:
        qc.add_register(AncillaRegister(1))
        qc.mcx(xnor_qc.ancillas, qc.ancillas[-1])

        qc = qc.compose(xnor_qc.inverse(), xnor_qc.qubits)

    qc.name = 'Check_Same_Num'
    return qc

#def prep_cnz(nqubits, set_qubit_value = [] ,mode='noancilla'):
#    '''Prepare cnz circuit with vgiven values of the qubits\n
#    Returns the prepared circuit\n
#    set_value_list contains a list of tuples that contains (qubit_index , 0 or 1)'''
#    
#    x_qubit = [value[0] for value in set_qubit_value if value[1] and value[0] < nqubits]
#
#    cnz_qc = cnz(nqubits, mode)
#
#    qc = QuantumCircuit(cnz_qc.qubits)
#    qc.x(x_qubit) if len(x_qubit) else None
#    qc.barrier(qc.qubits)
#    qc = qc.compose(cnz_qc, qc.qubits)
#    qc.barrier(qc.qubits)
#    qc.x(x_qubit) if len(x_qubit) else None
#
#    qc.name = f"cnz {nqubits}"
#    return qc

def create_sudoko_iteration(max_value = 2):
    max_cells = list(range(pow(max_value, 2)))
    qubit_num = (max_value - 1).bit_length()
    if not qubit_num:
        return None
    
    pairs = get_matrix_pairs(max_value)
    qubit_list = QuantumRegister(len(max_cells) * qubit_num)
    anc_list = AncillaRegister(qubit_num) if qubit_num > 1 else []

    answer_anc_list = []

    qc_pair = QuantumCircuit(qubit_list, anc_list)

    for p in pairs:
        check_equal_qc = check_same_num(qubit_num)
        answer_anc_list.append(check_equal_qc.ancillas[-1])
        qc_pair.add_register([answer_anc_list[-1]])
        
        qubit_connection = list(qubit_list[p[0] * qubit_num : (p[0] + 1) * qubit_num]) + list(qubit_list[p[1] * qubit_num : (p[1] + 1) * qubit_num]) + list(anc_list) + [check_equal_qc.ancillas[-1]]
        qc_pair = qc_pair.compose(check_equal_qc, qubit_connection)
        qc_pair.barrier(qc_pair.qubits)
    
    qc_z = cnz(len(answer_anc_list), [(i, 0) for i in range(len(answer_anc_list))])

    diffuser_qc = diffuser(len(get_qubit_list(qc_pair)))
    
    qc = QuantumCircuit(qc_pair.qubits)
    qc = qc.compose(qc_pair, qc_pair.qubits)
    qc.barrier(qc.qubits)
    qc = qc.compose(qc_z, answer_anc_list)
    qc.barrier(qc.qubits)
    qc = qc.compose(qc_pair.inverse(), qc_pair.qubits)
    qc.barrier(qc.qubits)
    qc = qc.compose(diffuser_qc, get_qubit_list(qc))

    return qc

def create_sudoko_circuits(max_value = 2, set_qubit_value = []):
    qc_iter = create_sudoko_iteration(max_value)
    return generate_grover_circuits_with_iterations(qc_iter, set_qubit_value)

def get_matrix_pairs(matrix_size = 4, start_cell = 0):
    output = []
    if start_cell >= pow(matrix_size, 2):
        return output

    cur_index = start_cell + 1
    while cur_index % matrix_size:
        pair = (start_cell, cur_index)
        output.append(pair) if pair not in output else None
        cur_index = cur_index + 1

    cur_index = start_cell + matrix_size
    while cur_index < pow(matrix_size, 2):
        pair = (start_cell, cur_index)
        output.append(pair) if pair not in output else None
        cur_index = cur_index + matrix_size

    output = output + [i for i in get_matrix_pairs(matrix_size=matrix_size, start_cell= start_cell + 1) if i not in output]

    return output

def check_under_nine(nqubits):
    '''Returns a circuit that calculates if the value of the qubits are under nine (0 - 8)\n
    The answer will be on the final ancilla bit.\n
    The ancillas, except the last one (Answer), can be reused'''
    nine_bit_size = int(9).bit_length()
    additional_qubits = nqubits - nine_bit_size
    if additional_qubits < 0:
        return None
    
    nand_three = mand_gate(3, [1] * 3)
    nand_three.x(nand_three.ancillas[-1])
    nand_three.barrier(nand_three.qubits)

    nand_fourth = nand_gate()
    
    nine_qubit_qc = QuantumCircuit(nand_three.qubits, nand_fourth.qubits[1:])
    nine_qubit_qc = nine_qubit_qc.compose(nand_three, nand_three.qubits)
    nine_qubit_qc = nine_qubit_qc.compose(nand_fourth, [nand_three.ancillas[-1]] + list(nand_fourth.qubits[1:]))

    if additional_qubits:
        add_qubits = QuantumRegister(additional_qubits)
        nine_qubit_qc.add_register(add_qubits)

        nine_qubit_qc.x(add_qubits)

        qc = QuantumCircuit(nine_qubit_qc.qubits, AncillaRegister(1))
        qc = qc.compose(nine_qubit_qc, nine_qubit_qc.qubits)
        qc.barrier(qc.qubits)
        qc.mcx(list(add_qubits) + [nine_qubit_qc.ancillas[-1]],  qc.ancillas[-1])
        qc.barrier(qc.qubits)
        qc = qc.compose(nine_qubit_qc.inverse(), nine_qubit_qc.qubits)     
    else:
        qc = QuantumCircuit(nine_qubit_qc.qubits)
        qc = qc.compose(nine_qubit_qc, nine_qubit_qc.qubits)
        qc = qc.compose(nand_three.inverse(), nand_three.qubits)

    qc.name = "Check_under_nine"
    return qc

#x, y =create_sudoko_circuits(4)
#print(x)
#print(x)
#print(y)

#print(simulate_grover_qc_list(x, y))

#z = QuantumOperation()
#print(x[-1].draw())
#z.set_circuit(x[y])
#print(z.get_circuit())
#print(z.run_circuit())