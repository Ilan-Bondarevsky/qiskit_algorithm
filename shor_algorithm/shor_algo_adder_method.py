import numpy as np

from qiskit import BasicAer, execute
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, AncillaRegister
from qiskit.tools.visualization import plot_histogram
from qiskit.circuit.gate import Gate

import bit_functions


def condition_phase_shift(k):
    qc = QuantumCircuit(2) #control qbit and qbit to oparate on

    angle = np.pi / (2**(k-1))
    qc.cp(angle, 0, 1)

    qc.name = str(k)
    return qc

qc = QuantumCircuit(3)

def adder(a, b):
    a_bits = bit_functions.bit_length(a)
    b_bits = bit_functions.bit_length(b)
    qc = QuantumCircuit(QuantumRegister(a_bits), AncillaRegister(b_bits))

    for j in range(b_bits):
        for k, i in enumerate(range(a_bits-1-j, -1, -1)):
            k += 1
            angle = 2*np.pi / (2**k) # k starts from 0 but in the article in start from 1
            qc.cp(angle, i, a_bits+b_bits-1-j, label=str(k))

    qc.name = f"adder({a})"
    return qc

def qft(n):
    """n-qubit QFT the first n qubits in circ"""
    qc = QuantumCircuit(n)
    for j in range(n-1, -1, -1):
        qc.h(j)
        for m in range(j-1, -1, -1):
            qc.cp(np.pi/float(2**(j-m)), j, m, label=f"{j-m+1}")
        qc.barrier()
    # Don't forget the Swaps!
    for qubit in range(n//2):
        qc.swap(qubit, n-qubit-1)

    # print(qc.draw())
    qc.name = "QFT"
    return qc

def qft_dagger(n):
    """n-qubit QFTdagger the first n qubits in circ"""
    qc = QuantumCircuit(n)
    # Don't forget the Swaps!
    for qubit in range(n//2):
        qc.swap(qubit, n-qubit-1)
    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi/float(2**(j-m)), m, j)
        qc.h(j)
    qc.name = "QFT†"
    return qc

a = 4
qc = qft(5)

print(qc.draw())


# qc.append(adder(1), [0, 1])
# qc.append(condition_phase_shift(1), [0, 2])
# qc.append(condition_phase_shift(1), [1, 0])

# qc.cp(math.pi / (2**(2-1)), 0, 1)
# qc.cp(2*math.pi / (2**1), 2, 1)
# qc.cp(2*math.pi / (2**1), 0, 2)

# print(qc.draw())