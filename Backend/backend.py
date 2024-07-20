import sys
import os
current_dir = os.getcwd()
sys.path.append(current_dir)
from quantum_circuit import QuantumCircuit
from qiskit import transpile as qiskit_transpiler
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import CouplingMap
from tooltip import copy_docs_and_signature_from
from qiskit.circuit.library import standard_gates
from itertools import permutations

class Backend():
    def __init__(self, num_qubits : int = 1, coupling_map : list[list[int]] | CouplingMap | None = None, 
                 basis_gates : list[str] = ["id", "rz", "sx", "x", "cx", "rx", "ry","h","u3", "u", "u1", "u2", "p"]) -> None:
        standard_gate_dict = Backend.get_standard_gate_list()
        basis_gates = set(basis_gates)
        if not basis_gates.issubset(set(standard_gate_dict.keys())):
            raise Exception("Not all chosen Basis Gates are valid, look at Standard gate List for valid information")
        self.backend = GenericBackendV2(num_qubits=num_qubits, coupling_map=coupling_map, basis_gates=list(basis_gates), calibrate_instructions = False)
        
        # prop = {
        #     tuple(connection) : None
        #     for connection in list(permutations(range(standard_gate_dict['ccx'].num_qubits)))
        # }
        # self.backend._target.add_instruction(standard_gate_dict['ccx'], prop)
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
                                                 original_qc_depth = qc.depth(), transpiled_qc_depth = transpiled_qc.depth(),
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
    
    def run(self, qc : QuantumCircuit, shots : int=1024, seed_simulator : int | None = None, **kwargs):
        return self.backend.run(qc, shots=shots, seed_simulator = seed_simulator, **kwargs)
    
    @staticmethod
    def get_standard_gate_list() ->dict:
        return standard_gates.get_standard_gate_name_mapping()
    
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

    def to_dict(self, ignore_attr : list[str] = []):
        return {attr: getattr(self, attr) for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__") and attr not in ignore_attr}           
            
if __name__ == "__main__":
    backend = Backend(3)
    # y=backend.get_backend()
    # for x,n in y.items():
    #     print(f"{x} : {n}")
    
    # x = ["id", "rz", "sx", "x", "cx", "rx", "ry","h","u3", "u", "u1", "u2", "p"]
    # y = Backend.get_standard_gate_list()
    # z = Backend(4, basis_gates=x)
    # for m in x:
    #     print(y[m].num_qubits)
    #     print(y[m].name)
    #     print()
    qc = QuantumCircuit(3)
    # qc.x(0)
    # qc.h(1)
    qc.ccx(0,1,2)
    # # qc.measure_all()
    print(qc.draw())
    job = backend.run(qc)
    # print(job.result())
    qc_transpile_pram = backend.transpile_save_param(qc, search_input=5)

    print(qc_transpile_pram.transpiled_qc.draw())
    print(qc_transpile_pram)
    # print(qc_transpile_pram.to_dict())
    # print(qc_transpile_pram.to_dict(['backend', 'transpiled_qc','original_qc']))

    # print(qc_transpile.draw())
    # job = backend.execute(qc_transpile)
    # print(job.result())
    