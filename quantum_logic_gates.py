from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister

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

#def mor_gate(nqubits, values = []):
#    '''Create an OR gate in qiskit with multiple qubits\n
#    The values in the list are corresponding to the qubits, the values (0/1)'''
#    qc = QuantumCircuit(QuantumRegister(nqubits), AncillaRegister(1))
#    
#    for i, val in enumerate(values):
#        if val:
#            qc.x(i)
#    
#    circuits = []
#
#    l = list(range(nqubits))
#    for length in range(1, 1 + nqubits):
#        for i in range(nqubits):
#            x= l[i : i + 1]
#            for j in range(i + 1, nqubits):
#                cur_l = x + l[j : j + length - 1]
#                circuits.append(cur_l) if cur_l not in circuits else None
#            circuits.append(x) if x not in circuits else None
#
#    for circ in circuits:
#        qc.mcx(circ, qc.ancillas)
#
#    return qc