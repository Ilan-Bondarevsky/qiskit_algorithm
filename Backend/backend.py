from qiskit import transpile, QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import CouplingMap


class BACKEND():
    def __init__(self, num_qubits : int = 1, coupling_map : list[list[int]] | CouplingMap | None = None) -> None:
        self.backend = GenericBackendV2(num_qubits=num_qubits, coupling_map=coupling_map)
        self.num_qubits = num_qubits
        self.coupling_map = coupling_map
      
    def get_backend(self):
        return self.backend
    
    def traspile_qiskit(self, list_qc : list[QuantumCircuit] | QuantumCircuit, optimization_level : list[int] | int = 3, initial_layout : list[list[int]] | list[int] | None = None) -> list[QuantumCircuit]:
        list_qc = list_qc if isinstance(list_qc, list) else [list_qc]
        optimization_level = optimization_level if isinstance(optimization_level, list) else [optimization_level]
        if initial_layout is None or not isinstance(initial_layout[0],list):
            initial_layout = [initial_layout]
        transpiled_qc_list = []
        for qc in list_qc:
            for level in optimization_level:
                for layout in initial_layout:
                    cur_qc = transpile(circuits=qc, backend=self.backend, optimization_level=level, initial_layout=layout)
                    transpiled_qc_list.append(cur_qc) 
                    transpiled_qc_list[-1].name = f"{self.backend.name} | {layout} | {level}" 
        return transpiled_qc_list
    
    def get_backend_qubits(self) -> int:
        return self.backend.num_qubits
    
    def get_backend_coupling_map(self) -> CouplingMap | list[list[int]]:
        return self.backend.coupling_map
    
    def execute(self, qc : QuantumCircuit, shots : int=1024):
        return self.backend.run(qc, shots=shots)

if __name__ == "__main__":
    backend = BACKEND(3)
    qc = QuantumCircuit(2)
    qc.x(0)
    qc.h(1)
    qc.measure_all()
    print(qc.draw())
    job = backend.execute(qc)
    print(job.result())
    
    qc_transpile = backend.traspile_qiskit(qc)[0]
    print(qc_transpile.draw())
    job = backend.execute(qc_transpile)
    print(job.result())
    