from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister

def cnz(qubits, mode = 'noancilla'):
    '''Create a contorl not Z (cnz) circuit based on the number of qubits.'''
    qc = QuantumCircuit(QuantumRegister(qubits, 'cnz_q'))

    if qubits < 1:
        return None
    
    if qubits == 1:
        qc.z(qc.qubits[0])
    elif qubits == 2:
        qc.cz(qc.qubits[0], qc.qubits[1])
    else:
        if mode == 'noancilla':
            qc.h(qubits-1)
            qc.mcx(list(range(qubits-1)), qubits-1)
            qc.h(qubits-1)
        else:
            ancilla = qubits - 2
            qc.add_register(AncillaRegister(ancilla, 'cnz_anc'))
            mid_q = (ancilla + qubits) // 2 - 1
            for i in range(ancilla):
                qc.ccx(mid_q - i, mid_q + i + 1, mid_q + i + 2)

            qc.cz(0, qubits + ancilla - 1)

            for i in list(range(ancilla))[::-1]:
                qc.ccx(mid_q - i, mid_q + i + 1, mid_q + i + 2)

    qc.name = f"cnz {qubits}"
    return qc

def set_value_circuit(nqubits, qubit_value_list = [], rest_hadamard=False):
    '''Returns a circuit of qubits when seting their values.\n
    In the qubit_value_list , each element is a tuple with index and value = (index, value)\n
    The default value of the qubits in qiskit is 0, zero.\n
    rest_hadamard, put the indexes that werent mentioned in the list with a hadamard gate.'''
    qc = QuantumCircuit(nqubits)
    
    if rest_hadamard:
        h_list = [index for index in range(nqubits) if index not in  [i[0] for i in qubit_value_list]]
        qc.h(h_list) if len(h_list) else None
    
    one_qubit = [index[0] for index in qubit_value_list if index[1] and index[0] < nqubits]
    qc.x(one_qubit) if len(one_qubit) else None
    
    return qc