from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister

def cnz(qubits, set_qubit_value = [], mode = 'noancilla'):
    '''Create a contorl not Z (cnz) circuit based on the number of qubits.\n
    Preparing the qubits values using a tuple (qubit_index , 0 or 1)'''
    qc = QuantumCircuit(QuantumRegister(qubits, 'cnz_q'))

    zero_qubit = [value[0] for value in set_qubit_value if not value[1] and value[0] < qubits]

    if qubits < 1:
        return None
    
    qc.x(zero_qubit) if len(zero_qubit) else None
    qc.barrier(qc.qubits)
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
    qc.barrier(qc.qubits)
    qc.x(zero_qubit) if len(zero_qubit) else None

    qc.name = f"cnz {qubits}"
    return qc