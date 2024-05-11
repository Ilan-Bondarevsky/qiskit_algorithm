from qiskit import QuantumCircuit as QuantumCircuit_Original
from qiskit.quantum_info import Operator, Statevector, DensityMatrix, StabilizerState

class QuantumCircuit(QuantumCircuit_Original):
    def get_unitary_matrix(self, input_dims=None, output_dims=None):
        return Operator(self, input_dims, output_dims).data
    
    def get_density_matrix(self, dims: int | tuple | list | None = None):
        return DensityMatrix(self, dims)
    
    def get_state_vector(self, dims: int | tuple | list | None = None):
        return Statevector(self, dims)
    
    def get_stabilizer_state(self, validate: bool = True):
        return StabilizerState(self, validate)


if __name__ == "__main__":
    qc = QuantumCircuit(2)
    qc.x(0)
    qc.h(1)
    for func in [qc.draw, qc.get_unitary_matrix, qc.get_density_matrix, qc.get_stabilizer_state, qc.get_state_vector]:
        print(f"### Function : {func.__name__} ###")
        print(func())
        print()
    # print(qc.draw())
    # print(qc.get_unitary_matrix())
    # print(qc.get_density_matrix())
    # print(qc.get_state_vector())
    # print(qc.get_stabilizer_state())