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

def adder_classic_a(n, a, kind = "fixed"): #n is the number of qubits requer for one number
    qc = QuantumCircuit(QuantumRegister(n + (1 if kind == "half" else 0)))
    bit_field_a = bit_functions.full_bitfield(a, n)

    for j in range(n):
        if bit_field_a[n-1-j] == 1:
            for k in range(j, n):
                power = k - j + 1
                angle = 2*np.pi / (2**power) # k starts from 0 but in the article in start from 1
                qc.p(angle, k)
        # qc.barrier()

    if kind == "half":
        for i in range(n):
            if bit_field_a[n-1-i] == 1:
                angle = 2*np.pi / (2**(n-i+1))
                qc.p(angle, n)

    qc = qc.to_gate()
    qc.name = f"ɸ ADD_{a}"
    return qc

def subtracter_classic_a(n, a):
    qc = adder_classic_a(n, a, "half").inverse()
    qc.name = f"ɸ SUB_{a}"
    return qc

def qft(n, swap = True):
    """n-qubit QFT the first n qubits in circ"""
    qc = QuantumCircuit(n)
    for j in range(n-1, -1, -1):
        qc.h(j)
        for m in range(j-1, -1, -1):
            qc.cp(np.pi/float(2**(j-m)), j, m, label=f"{j-m+1}")
        # qc.barrier()
    # Don't forget the Swaps!
    if swap:
        for qubit in range(n//2):
            qc.swap(qubit, n-qubit-1)

    qc = qc.to_gate()
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
    qc = qc.to_gate()
    qc.name = "QFT†"
    return qc

def add_mod_n(a, N):
    n = bit_functions.bit_length(N)

    qr = QuantumRegister(n+3)
    ar = AncillaRegister(1)

    qc = QuantumCircuit(qr, ar)

    qc.append(adder_classic_a(n, a, "half").control(2), [0, 1] + list(range(2, n+3)))
    qc.append(subtracter_classic_a(n, N), range(2, n+3))
    qc.append(qft_dagger(n+1, False), range(2, n+3))
    qc.cx(n+2, n+3)
    qc.append(qft(n+1, False), range(2, n+3))
    qc.append(adder_classic_a(n, N, "half").control(1), [n+3] + list(range(2, n+3)))

    qc.append(subtracter_classic_a(n, a).control(2), [0, 1] + list(range(2, n+3)))
    qc.append(qft_dagger(n+1, False), range(2, n+3))
    qc.x(n+2)
    qc.cx(n+2, n+3)
    qc.x(n+2)
    qc.append(qft(n+1, False), range(2, n+3))
    qc.append(adder_classic_a(n, a, "half").control(2), [0, 1] + list(range(2, n+3)))

    qc = qc.to_gate()
    qc.name = f"ɸ ADD_{a}_mod_{N}"
    return qc

def c_mult_a_mod_n(a, N):
    n = bit_functions.bit_length(N)
    qr = QuantumRegister(2*n+4)
    qc = QuantumCircuit(qr)

    qc.append(qft(n+1, False), range(n+2, 2*n+3))

    for i in range(n):
        number = (a * 2**i)%N
        qc.append(add_mod_n(number, N), [0, i+1] + list(range(n+2, 2*n+4)))

    qc.append(qft_dagger(n+1, False), range(n+2, 2*n+3))
    qc.name = f"CMULT({a}) mod {N}"
    return qc

def inverse_c_mult_a_mod_n(a, N):
    qc = c_mult_a_mod_n(a, N).inverse()
    qc.name = f"CMULT({a}) mod {N}†"
    return qc

def U(a, N):
    n = bit_functions.bit_length(N)
    qc = QuantumCircuit(2*n + 4)
    qc.append(c_mult_a_mod_n(a, N), range(2*n + 4))
    
    qc.barrier()
    
    for i in range(1, n+2):
        qc.cswap(0, i, i+n+1, label=f'{i} to {i+n}')

        qc.barrier()

    if np.gcd(a, N) != 1:
        raise ArithmeticError(f"inverse of {a} mod {N} doesn't exists")
    i_a = pow(a, -1, N)
    qc.append(inverse_c_mult_a_mod_n(i_a, N), range(2*n+4))


    qc.name = f"U{a}"
    return qc

if __name__ == "__main__":

    qc = c_mult_a_mod_n(3, 15)

    print(qc.draw())

