from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister , Aer, execute, ClassicalRegister

from itertools import combinations

def and_gate(a = 0 , b = 0):
    '''Create an AND gate in qiskit\n
    The values of "a" and "b" are inisializing the qubits, the values (0/1)'''
    qc = QuantumCircuit(QuantumRegister(2), AncillaRegister(1))
    if a:
        qc.x(0)
    if b:
        qc.x(1)
    qc.mcx([0,1], qc.ancillas)
    return qc

def nand_gate(a = 0 , b = 0):
    '''Create an NAND gate in qiskit\n
    The values of "a" and "b" are inisializing the qubits, the values (0/1)'''
    qc = QuantumCircuit(QuantumRegister(2), AncillaRegister(1))
    if a:
        qc.x(0)
    if b:
        qc.x(1)
    qc.mcx([0,1], qc.ancillas)
    qc.x(qc.ancillas)
    return qc

def mand_gate(nqubits, values = []):
    '''Create an AND gate in qiskit with multiple qubits\n
    The values in the list are corresponding to the qubits, the values (0/1)'''
    qc = QuantumCircuit(QuantumRegister(nqubits), AncillaRegister(1))
    
    for i, val in enumerate(values):
        if val:
            qc.x(i)
    
    qc.mcx(list(range(nqubits)), qc.ancillas)   
    return qc

def xor_gate(a = 0 , b = 0):
    '''Create an XOR gate in qiskit\n
    The values of "a" and "b" are inisializing the qubits, the values (0/1)'''
    qc = QuantumCircuit(QuantumRegister(2), AncillaRegister(1))
    if a:
        qc.x(0)
    if b:
        qc.x(1)
    qc.cx(0, qc.ancillas)
    qc.cx(1, qc.ancillas)
    return qc

def xnor_gate(a = 0 , b = 0):
    '''Create an XNOR gate in qiskit\n
    The values of "a" and "b" are inisializing the qubits, the values (0/1)'''
    qc = QuantumCircuit(QuantumRegister(2), AncillaRegister(1))
    if a:
        qc.x(0)
    if b:
        qc.x(1)
    qc.cx(0, qc.ancillas)
    qc.cx(1, qc.ancillas)
    qc.x(qc.ancillas)
    return qc

def mxor_gate(nqubits, values = []):
    '''Create an XOR gate in qiskit with multiple qubits\n
    The values in the list are corresponding to the qubits, the values (0/1)'''
    qc = QuantumCircuit(QuantumRegister(nqubits), AncillaRegister(1))
    
    for i, val in enumerate(values):
        if val:
            qc.x(i)
    
    for i in range(nqubits):
        qc.cx(i, qc.ancillas)
  
    return qc

def or_gate(a = 0 , b = 0):
    '''Create an OR gate in qiskit\n
    The values of "a" and "b" are inisializing the qubits, the values (0/1)'''
    qc = QuantumCircuit(QuantumRegister(2), AncillaRegister(1))
    if a:
        qc.x(0)
    if b:
        qc.x(1)
    qc.cx(0, qc.ancillas)
    qc.cx(1, qc.ancillas)
    qc.mcx([0,1], qc.ancillas)
    return qc

def nor_gate(a = 0 , b = 0):
    '''Create an NOR gate in qiskit\n
    The values of "a" and "b" are inisializing the qubits, the values (0/1)'''
    qc = QuantumCircuit(QuantumRegister(2), AncillaRegister(1))
    if a:
        qc.x(0)
    if b:
        qc.x(1)
    qc.cx(0, qc.ancillas)
    qc.cx(1, qc.ancillas)
    qc.mcx([0,1], qc.ancillas)
    qc.x(qc.ancillas)
    return qc

def mor_gate(nqubits, values = []):
    '''Create an OR gate in qiskit with multiple qubits\n
    The values in the list are corresponding to the qubits, the values (0/1)'''
    qc = QuantumCircuit(QuantumRegister(nqubits), AncillaRegister(1))
    
    for i, val in enumerate(values):
        if val:
            qc.x(i)
    
    or_cirq = []
    for i in range(1, nqubits + 1):
        or_cirq = or_cirq + list(combinations(list(range(nqubits)), i))

    for circ in or_cirq:
        qc.mcx(list(circ), qc.ancillas)

    return qc