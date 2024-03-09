from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister, ClassicalRegister
from bit_functions import full_bitfield, get_qubit_list

from grover_cirq import grover_circuit
from logic_gate_circuits import xnor_gate
from backend_operation import run_simulator
from qiskit.tools.visualization import plot_histogram

class sudoko_grover(grover_circuit):
    def __init__(self, max_num : int = 4):
        super().__init__()
        self.max_num = max_num
        self.min_num = 1
        self.max_num_circuit = None

    def same_num_cirq(self):
        bit = self.max_num.bit_length()
        
        qubit_A = QuantumRegister(bit, 'A')
        qubit_B = QuantumRegister(bit, 'B')
        anc = AncillaRegister(bit + 1)
        qc = QuantumCircuit(qubit_A, qubit_B, anc)

        for i in range(bit):
            xnor_qc = xnor_gate()
            qc = qc.compose(xnor_qc, [qubit_A[i], qubit_B[i], anc[i]])
            
        inv_qc = qc.inverse() 
        qc.mcx(anc[:-1], anc[-1])
        qc = qc.compose(inv_qc, list(qubit_A) + list(qubit_B) + list(anc))

        return qc


    def calculation_logic(self):
        pass
    
    def build_iteration(self):
        pass


if __name__ == "__main__":
    x =  sudoko_grover()
    y=x.same_num_cirq()

    print(y.draw())
    y.add_register(ClassicalRegister(1))
    y.measure(y.qubits[-1],y.clbits[-1])
    print(y.draw())
    print(run_simulator(y).get_counts())