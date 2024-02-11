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
        self.max_num_circuit = None

    def same_num_cirq(self):
        bit = self.max_num.bit_length()
        
        qubit_A = QuantumRegister(bit, 'A')
        qubit_B = QuantumRegister(bit, 'B')
        anc = AncillaRegister(bit + 1)
        qc = QuantumCircuit(qubit_A, qubit_B, anc)

        qc.x(0)
        qc.x(4)
        for i in range(bit):
            xor_qc = xnor_gate()
            qc = qc.compose(xor_qc, [qubit_A[i], qubit_B[i], anc[i]])
        qc.mcx(anc[:-1], anc[-1])
        #for i in range(bit):
        #    xor_qc = xor_gate()
        #    qc = qc.compose(xor_qc, [qubit_A[i], qubit_B[i], anc[i]])

        return qc


    def calculation_logic(self):
        pass
    
    def build_iteration(self):
        pass


x = sudoko_grover(10)
z = x.same_num_cirq()
z.add_register(ClassicalRegister(1))
z.measure(z.qubits[-1], 0)
print(z)
y = run_simulator(z)
print(y.get_counts())