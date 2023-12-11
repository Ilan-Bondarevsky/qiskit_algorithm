def bitfield(num):
    '''Return a bit field of the given integer number'''
    return [int(digit) for digit in bin(num)[2:]] # [2:] to chop off the "0b" part

def full_bitfield(num, max_size=None):
    '''Return a bit field of an integer number with given size, will add zeroes if needed'''
    val = bitfield(num)
    max_size = len(val) if max_size is None else max_size
    if max_size < len(val):
        raise MemoryError("Out of bound memory")
    return [0] * (max_size - len(val)) + val

def get_qubit_list(quantum_circuit):
    '''Get a list of the qubits without the ancillas'''
    return list(filter(lambda q : q not in quantum_circuit.ancillas, quantum_circuit.qubits))