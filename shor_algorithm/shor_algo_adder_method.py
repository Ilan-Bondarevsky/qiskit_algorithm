import numpy as np

from qiskit import BasicAer, execute
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, AncillaRegister, Aer, transpile
from qiskit.tools.visualization import plot_histogram
from qiskit.circuit.gate import Gate

import sys
sys.path.insert(0, "D:/myProjects/AfekaCodeProjects/codeProjects/FinalProject_qiskit/qiskit_algorithm")

import bit_functions


def condition_phase_shift(k):
    qc = QuantumCircuit(2) #control qbit and qbit to oparate on

    angle = np.pi / (2**(k-1))
    qc.cp(angle, 0, 1)

    qc.name = str(k)
    return qc

qc = QuantumCircuit(3)

def set_start_state(qc, number, start_qubit):
    bin_num = bin(number)
    for i in range(1, len(bin_num)+1):
        if bin_num[-i] == '1':
            qc.x(i+start_qubit-1)
            
def adder(n, kind = "fixed"): #n is the number of qubits requer for one number
    qc = QuantumCircuit(QuantumRegister(n), AncillaRegister(n + (1 if kind == "half" else 0) ))

    for j in range(n):
        for k in range(j, n):
            power = k - j + 1
            angle = 2*np.pi / (2**power) # k starts from 0 but in the article in start from 1
            qc.cp(angle, j, n+k, label=str(power))
        # qc.barrier()

    if kind == "half":
        for i in range(n):
            angle = 2*np.pi / (2**(i+2))
            qc.cp(angle, n-1-i, 2*n)
    qc.name = f"ADD_{n}"
    return qc

def subtracter(n):
    qc = adder(n, "half").inverse()
    qc.name = f"SUB_{n}"
    return qc

def qft(n, swap = True):
    """n-qubit QFT the first n qubits in circ"""
    qc = QuantumCircuit(n)
    for j in range(n-1, -1, -1):
        qc.h(j)
        for m in range(j-1, -1, -1):
            qc.cp(np.pi/float(2**(j-m)), j, m, label=f"{j-m+1}")
        qc.barrier()
    # Don't forget the Swaps!
    if swap:
        for qubit in range(n//2):
            qc.swap(qubit, n-qubit-1)

    qc.name = "QFT"
    return qc

def qft_dagger(n, swap = True):
    """n-qubit QFTdagger the first n qubits in circ"""
    qc = QuantumCircuit(n)
    # Don't forget the Swaps!
    if swap:
        for qubit in range(n//2):
            qc.swap(qubit, n-qubit-1)
    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi/float(2**(j-m)), m, j)
        qc.h(j)
    qc.name = "QFT†"
    return qc





# qc = QuantumCircuit(6)

# a = 4
# b = 5

# # set_start_state(qc, a, 0)
# # set_start_state(qc, b, 3) 


# # qc.append(qft(3), range(3, 6))
# qc = qc.compose(adder(3), qubits=range(6))
# # qc.append(qft_dagger(6), range(6))

# # qc.measure_all()
# print(qc.draw())



# aer_sim = Aer.get_backend('aer_simulator')
# t_qc = transpile(qc, aer_sim)
# counts = aer_sim.run(t_qc).result().get_counts()
# print(plot_histogram(counts))




# qc.append(adder(1), [0, 1])
# qc.append(condition_phase_shift(1), [0, 2])
# qc.append(condition_phase_shift(1), [1, 0])

# qc.cp(math.pi / (2**(2-1)), 0, 1)
# qc.cp(2*math.pi / (2**1), 2, 1)
# qc.cp(2*math.pi / (2**1), 0, 2)

# print(qc.draw())