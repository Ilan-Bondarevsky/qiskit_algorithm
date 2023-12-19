from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister, ClassicalRegister, Aer, execute
from bit_functions import full_bitfield, get_qubit_list
from grover_cirq import diffuser, calculate_iteration, prep_search_qubits, check_solution_grover
from quantum_circuits import cnz
from quantum_logic_gates import and_gate, or_gate, xor_gate, xnor_gate, nand_gate, nor_gate, mor_gate
from quantum_operation import QuantumOperation
from grover_cirq import diffuser
from grover_num_list_cirq import num_oracle
import math
from itertools import combinations

def diffrent_num(nqubits):
    num_a = QuantumRegister(nqubits, 'num_a')
    num_b = QuantumRegister(nqubits, 'num_b')
    qc = QuantumCircuit(num_a, num_b)

    for i in range(nqubits):
        xor_qc = xor_gate()
        qc.add_register(xor_qc.ancillas)
        qc = qc.compose(xor_qc, [num_a[i] , num_b[i]] + list(xor_qc.ancillas))
    qc.name = 'Diff_Num'
    return qc

def check_under_ten_no_zero():
    nqubits = int(9).bit_length()
    qc = QuantumCircuit(nqubits)

    nand_g = nand_gate()
    add_anc = AncillaRegister(1)
    qc.add_register(add_anc)
    qc = qc.compose(nand_g.copy(), [1,3, qc.ancillas[-1]])

    qc.barrier(qc.qubits)
    add_anc = AncillaRegister(1)
    qc.add_register(add_anc)
    qc = qc.compose(nand_g.copy(), [2,3, qc.ancillas[-1]])

    qc.barrier(qc.qubits)

    add_anc = AncillaRegister(1)
    qc.add_register(add_anc)
    mor_g = mor_gate(nqubits)
    qc = qc.compose(mor_g.copy(), get_qubit_list(qc) + [qc.ancillas[-1]])
    qc.name = "Between 1-9 (with 1 & 9)"
    return qc

def sudoko_max_four(index_value_list=None):
    iteration = QuantumCircuit(pow(2, 4))
    comb = [list(x) for x in combinations(list(range(4)), 2)]

    for c in comb:
        diff_row = diffrent_num(2)
        diff_col = diffrent_num(2)
        iteration.add_register(list(diff_col.ancillas) + list(diff_row.ancillas))
        

    qc = QuantumCircuit(iteration.qubits)
    prep = prep_search_qubits(len(qc.qubits) , index_value_list)
    qc = qc.compose(prep, get_qubit_list(qc))
    return qc
    

print(sudoko_max_four())
###
qc_oracle = diffrent_num(3)

iteration_qc = QuantumCircuit(qc_oracle.qubits)

iteration_qc = iteration_qc.compose(qc_oracle, iteration_qc.qubits)

cz = cnz(len(iteration_qc.ancillas))

iteration_qc.add_register(cz.ancillas)

iteration_qc.barrier(iteration_qc.qubits)
iteration_qc = iteration_qc.compose(cz, list(iteration_qc.ancillas) + list(cz.ancillas))
iteration_qc.barrier(iteration_qc.qubits)

iteration_qc = iteration_qc.compose(qc_oracle.inverse(), iteration_qc.qubits)

iteration_qc.barrier(iteration_qc.qubits)

diff = diffuser(len(get_qubit_list(iteration_qc)))
iteration_qc.add_register(diff.ancillas)
iteration_qc = iteration_qc.compose(diff, get_qubit_list(iteration_qc) + list(diff.ancillas))
#####

qc = QuantumCircuit(iteration_qc.qubits)
qc.h(get_qubit_list(qc))

num_queries = math.floor((math.pi * math.sqrt(pow(2, len(get_qubit_list(qc))))) / 4)
num_queries = 1
for _ in range(num_queries):
    qc.barrier(qc.qubits)
    qc = qc.compose(iteration_qc, qc.qubits)

qc.add_register(ClassicalRegister(len(get_qubit_list(qc))))
qc.measure(get_qubit_list(qc), qc.clbits)

print(qc.draw())

run_qc = qc

result = execute(run_qc, backend = Aer.get_backend('aer_simulator'),shots=1024).result()
print(result.get_counts())

print([i for i in result.get_counts() if result.get_counts()[i] > 50])
print(sum([val for val in result.get_counts().values()]))
#print(diff.draw())
#qc.add_register(diff.ancillas)
#qc = qc.compose(diff, get_qubit_list(qc) + list(diff.ancillas))

