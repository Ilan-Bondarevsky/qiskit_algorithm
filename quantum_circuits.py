from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister
from bit_functions import full_bitfield

def cnz(qubits, mode = 'noancilla'):
    '''Create a contorl not Z (cnz) circuit based on the number of qubits'''
    qc = QuantumCircuit(QuantumRegister(qubits, 'qubit'))
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
            qc.add_register(AncillaRegister(ancilla, 'ancilla'))
            mid_q = (ancilla + qubits) // 2 - 1
            for i in range(ancilla):
                qc.ccx(mid_q - i, mid_q + i + 1, mid_q + i + 2)

            qc.cz(0, qubits + ancilla - 1)

            for i in list(range(ancilla))[::-1]:
                qc.ccx(mid_q - i, mid_q + i + 1, mid_q + i + 2)
    qc.name = "cnz " + str(qubits)
    return qc

def index_data_cirq(index, value, index_qubits, value_qubits):
    '''Create a circuit that create a connection between an index and a value in a circuit\n
    Each index has a specific value.'''
    qc = QuantumCircuit(QuantumRegister(index_qubits, 'index'), AncillaRegister(value_qubits, 'value'))
    index_bit_field = full_bitfield(index, index_qubits)[::-1]
    value_bit_field = full_bitfield(value, value_qubits)[::-1]

    qc.x([i for i, _ in enumerate(index_bit_field) if not index_bit_field[i]])

    for bit in [i for i, _ in enumerate(value_bit_field) if value_bit_field[i]]:
        qc.mcx(list(range(len(index_bit_field))), qc.ancillas[bit])

    qc.x([i for i, _ in enumerate(index_bit_field) if not index_bit_field[i]])
    
    qc.name = f"Index {index} : Value {value}"
    return qc 