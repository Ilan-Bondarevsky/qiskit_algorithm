from qiskit import QuantumCircuit as QiskitQuantumCircuit
from qiskit.quantum_info import Operator, Statevector, DensityMatrix, StabilizerState
from qiskit import QuantumCircuit, AncillaRegister, ClassicalRegister, QuantumRegister

class QuantumCircuit(QiskitQuantumCircuit):
    def get_unitary_matrix(self, input_dims=None, output_dims=None):
        return Operator(self, input_dims, output_dims).data
    
    def get_density_matrix(self, dims: int | tuple | list | None = None):
        return DensityMatrix(self, dims)
    
    def get_state_vector(self, dims: int | tuple | list | None = None):
        return Statevector(self, dims)
    
    def get_stabilizer_state(self, validate: bool = True):
        return StabilizerState(self, validate)
    
    @staticmethod
    def from_qiskit_circuit(qiskit_circuit : QiskitQuantumCircuit):
        custom_circuit = QuantumCircuit(qiskit_circuit.qubits)
        custom_circuit.add_register(qiskit_circuit.clbits)
        
        custom_circuit.data = qiskit_circuit.data.copy()  # Copy the operations
        custom_circuit.global_phase = qiskit_circuit.global_phase  # Copy the global phase
        custom_circuit.metadata = qiskit_circuit.metadata  # Copy the metadata if any
        return custom_circuit


if __name__ == "__main__":
    qc = QuantumCircuit(2)
    qc.x(0)
    qc.h(1)
    for func in [qc.draw, qc.get_unitary_matrix, qc.get_density_matrix, qc.get_stabilizer_state, qc.get_state_vector]:
        print(f"### Function : {func.__name__} ###")
        print(func())
        print()
        
    qc = QiskitQuantumCircuit(5)
    print(qc.draw())
    qc = QuantumCircuit.from_qiskit_circuit(qc)
    print(qc.draw())
    # print(qc.draw())
    # print(qc.get_unitary_matrix())
    # print(qc.get_density_matrix())
    # print(qc.get_state_vector())
    # print(qc.get_stabilizer_state())