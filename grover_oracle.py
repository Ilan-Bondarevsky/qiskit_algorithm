from qiskit import QuantumCircuit, AncillaRegister, QuantumRegister
from bit_functions import full_bitfield, get_qubit_list
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