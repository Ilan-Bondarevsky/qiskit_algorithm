from qiskit import QuantumCircuit
from quantum_circuits import cnz
from bit_functions import full_bitfield

#https://arxiv.org/pdf/1502.04943.pdf

def num_list_oracle(winner_list, max_list_value, mode = 'noancilla', block_diagram=True):
    '''Create a circquit to reflect the qubits when the input is one of the winning numbers.\n
    The max qubits is based on the max value given\n
    Can return the CNZ circuit to be a gate block or shhow its full circuit using BLOCK_DIAGRAM'''
    qc = QuantumCircuit(len(full_bitfield(max_list_value)))
    #qc = QuantumCircuit(len(full_bitfield(max(winner_list), nqubits)))
    for num in winner_list:
        if num > max_list_value:
            raise MemoryError("Winner value higher than max value!")
        
        qc.barrier(qc.qubits)
        bit_list = full_bitfield(num, len(qc.qubits))[::-1]
        
        neg_bit = [i for i,_ in enumerate(bit_list) if not bit_list[i]]
        qc.x(neg_bit) if len(neg_bit) else None
        
        if block_diagram:
            qc.append(cnz(len(qc.qubits), mode), qc.qubits)
        else:
            qc.barrier(qc.qubits)
            qc = qc.compose(cnz(len(qc.qubits), mode), qc.qubits)   
            qc.barrier(qc.qubits)
    
        qc.x(neg_bit) if len(neg_bit) else None
        qc.barrier(qc.qubits)

    qc.name = 'Oracle_Num ' + str(winner_list)
    return qc

