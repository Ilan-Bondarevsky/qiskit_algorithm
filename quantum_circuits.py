from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister
from bit_functions import get_qubit_list

def cnz(qubits, mode = 'noancilla'):
    '''Create a contorl not Z (cnz) circuit based on the number of qubits'''
    qc = QuantumCircuit(QuantumRegister(qubits, 'cnz_q'))
    if qubits < 1:
        return None
    elif qubits == 1:
        qc.z(qubits-1)
    elif qubits == 2:
        qc.cz(qubits-2, qubits-1)
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
    qc.name = "cnz " + str(qubits)
    return qc

def z_or(nqubits, mode='noancilla'):
    cz = cnz(nqubits, mode)
    qc = QuantumCircuit(cz.qubits)
    qc.x(get_qubit_list(qc))
    qc.barrier(qc.qubits)
    qc = qc.compose(cz, qc.qubits)
    qc.barrier(qc.qubits)
    qc.x(get_qubit_list(qc))
    qc.name = f"Zor {nqubits}"
    return qc