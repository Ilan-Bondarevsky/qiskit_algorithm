import sys
import os
current_dir = os.getcwd()
sys.path.append(current_dir)
from quantum_circuit import QuantumCircuit
from qiskit import transpile as qiskit_transpiler
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import CouplingMap
from tooltip import copy_docs_and_signature_from
    
class Backend():
    def __init__(self, num_qubits : int = 1, coupling_map : list[list[int]] | CouplingMap | None = None) -> None:
        self.backend = GenericBackendV2(num_qubits=num_qubits, coupling_map=coupling_map)
        self.num_qubits = num_qubits
        self.coupling_map = coupling_map
      
    def get_backend(self):
        return self.backend
    
    @copy_docs_and_signature_from(qiskit_transpiler)
    def transpile(self, qc : QuantumCircuit, optimization_level : int = 3, initial_layout = None, seed_transpiler : int = None, **kwargs) ->QuantumCircuit:
        transpiled_qc = qiskit_transpiler(circuits=qc, backend=self.backend, optimization_level=optimization_level, initial_layout=initial_layout, 
                                          seed_transpiler=seed_transpiler, **kwargs)
        return QuantumCircuit.from_qiskit_circuit(transpiled_qc)

    @copy_docs_and_signature_from(qiskit_transpiler)
    def transpile_save_param(self, qc : QuantumCircuit, optimization_level : int = 3, initial_layout = None, seed_transpiler : int = None, **kwargs):
        save_input = {
            key : val
            for key, val in kwargs.items() if 'input' in key
        }
        for key in save_input:
            kwargs.pop(key)
        transpiled_qc = self.transpile(qc, optimization_level=optimization_level, initial_layout=initial_layout, seed_transpiler=seed_transpiler, **kwargs)
        kwargs.update(save_input)
        return saved_transpile_action_parameters(original_qc=qc, transpiled_qc=transpiled_qc, optimization_level=optimization_level, 
                                                 initial_layout=initial_layout, seed_transpiler=seed_transpiler, backend=self, backend_name = self.backend.name,
                                                 **kwargs)
    
    @copy_docs_and_signature_from(qiskit_transpiler)
    def traspile_qiskit(self, list_qc : list[QuantumCircuit] | QuantumCircuit, optimization_level : list[int] | int = 3, initial_layout : list[list[int]] | list[int] | None = None, **kwrags) -> list[QuantumCircuit]:
        list_qc = list_qc if isinstance(list_qc, list) else [list_qc]
        optimization_level = optimization_level if isinstance(optimization_level, list) else [optimization_level]
        if initial_layout is None or not isinstance(initial_layout[0],list):
            initial_layout = [initial_layout]
        transpiled_qc_list = []
        for qc in list_qc:
            for level in optimization_level:
                for layout in initial_layout:
                    cur_qc = qiskit_transpiler(circuits=qc, backend=self.backend, optimization_level=level, initial_layout=layout, **kwrags)
                    transpiled_qc_list.append(cur_qc) 
                    transpiled_qc_list[-1].name = f"{self.backend.name} | {layout} | {level}" 
        return transpiled_qc_list
    
    def get_backend_qubits(self) -> int:
        return self.backend.num_qubits
    
    def get_backend_coupling_map(self) -> CouplingMap | list[list[int]]:
        return self.backend.coupling_map
    
    def run(self, qc : QuantumCircuit, shots : int=1024, **kwargs):
        return self.backend.run(qc, shots=shots, **kwargs)

class saved_transpile_action_parameters:
    def __init__(self, original_qc : QuantumCircuit = None, transpiled_qc : QuantumCircuit = None, optimization_level : int | None = None, 
                 initial_layout : dict | list | None= None, seed_transpiler : int | None = None, backend : Backend = None, **kwargs) -> None:
        self.backend = backend
        self.original_qc = original_qc
        self.transpiled_qc = transpiled_qc
        self.optimization_level = optimization_level
        self.initial_layout = initial_layout
        self.seed_transpiler = seed_transpiler
        
        for key, value in kwargs.items():
            setattr(self, key, value)
            
            
if __name__ == "__main__":
    backend = Backend(3)
    qc = QuantumCircuit(2)
    qc.x(0)
    qc.h(1)
    qc.measure_all()
    print(qc.draw())
    job = backend.run(qc)
    print(job.result())
    qc_transpile_pram = backend.transpile_save_param(qc, search_input=5)

    # print(qc_transpile.draw())
    # job = backend.execute(qc_transpile)
    # print(job.result())
    