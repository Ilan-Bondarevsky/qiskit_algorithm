from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister
from quantum_cirq_func import get_qubit_list, cnz
from grover import Grover

def bitfield(n):
    return [int(digit) for digit in bin(n)[2:]] # [2:] to chop off the "0b" part
def full_bitfield(size, n):
    val = bitfield(n)
    if size >= len(val):
        return [0] * (size - len(val)) + val
    else:
        raise MemoryError("Out of bound memory")
  
class DataListGrover(Grover):
    def __init__(self, data_list, winner_list, prep_func=None):
        super().__init__(prep_func=prep_func, oracle_func=self.num_oracle, data_func=self.num_list_data, iteration_func=self.combine_data_oracle)
        self.data = data_list
        self.winner = winner_list
    
    def create_data(self, mode='noancilla'):
        return super().create_data(data_list=self.data ,mode=mode)
    
    def create_oracle(self, nqubits, mode='noancilla'):
        return super().create_oracle(nqubits=nqubits, mode=mode, num_list=self.winner)

    def num_oracle(self, nqubits,num_list=None, mode = 'noancilla'):
        #https://arxiv.org/pdf/1502.04943.pdf
        if num_list is not None:
            self.winner = num_list
        if not isinstance(self.winner, list):
            self.winner = [self.winner]
        if nqubits is None:
            nqubits = max([bitfield(n) for n in self.winner], key=lambda x : len(x))
            nqubits = len(nqubits)
        qc = QuantumCircuit()
        for num in self.winner:
            bit_list = bitfield(num)
            bit_list = bit_list[::-1] + [0] * (nqubits - len(bit_list))
            
            if len(bit_list) > nqubits:
                return None
            neg_bit = [i for i,_ in enumerate(bit_list) if not bit_list[i]]
            z = cnz(nqubits, mode)
            qc.add_register(z.qubits)

            qc.x(neg_bit) if len(neg_bit) else None
            qc.barrier(qc.qubits)
            qc = qc.compose(z, qc.qubits)    
            qc.barrier(qc.qubits)     
            qc.x(neg_bit) if len(neg_bit) else None

        #q = AncillaRegister(1)
        #qc.add_register(q)
        #qc.h(q)
        #qc.mcx(get_qubit_list(qc),q)
        #qc.h(q)

        qc.name = 'Oracle_Num_' + str(num)
        return qc
    
    def num_list_data(self, data_list=None, mode = 'noancilla'):
        if data_list is not None:
            self.data = data_list
        if self.data is None:
            return None
        if not isinstance(self.data, list):
            self.data = [self.data]
        
        qc = QuantumCircuit(QuantumRegister(len(bitfield(len(self.data) - 1)), 'Index'),
                            AncillaRegister(len(bitfield(max(self.data))), "Data"))

        for i,val in enumerate(self.data):
            qc.barrier(qc.qubits)
            try:
                bit_index = full_bitfield(qc.num_qubits - qc.num_ancillas, i)[::-1]
                for qubit in [k for k,_ in enumerate(bit_index) if not bit_index[k]]:
                    qc.x(qubit)

                bit_data = full_bitfield(qc.num_ancillas, val)[::-1]

                for qubit in [k for k,_ in enumerate(bit_data) if bit_data[k]]:
                    qc.mcx(list(filter(lambda q : q not in qc.ancillas, qc.qubits)),
                        qc.ancillas[qubit])

                for qubit in [k for k,_ in enumerate(bit_index) if not bit_index[k]]:
                    qc.x(qubit)
            except MemoryError as e:
                print(f"An exception occurred: {str(e)}")

        qc.name = 'Array_Data'
        return qc
    
    def combine_data_oracle(self, oracle=None, data =None):
        if oracle is None:
            return None
        qc_oracle = oracle.copy()
        if data is None:
            return qc_oracle
        
        qc_data = data.copy()
        
        qc = QuantumCircuit(data.qubits)
        qc = qc.compose(qc_data, qc.qubits)
        qc.add_register(qc_oracle.ancillas)
        qc.barrier(qc.qubits)
        qc = qc.compose(qc_oracle, qc_data.ancillas[:] + qc_oracle.ancillas[:])
        qc.barrier(qc.qubits)
        qc = qc.compose(qc_data.inverse(), get_qubit_list(qc_data)[:] + qc_data.ancillas[:])
        qc.name = 'iteration'
        return qc