from qiskit import Aer, execute, ClassicalRegister
import qiskit.providers.fake_provider
from qiskit.tools.visualization import plot_histogram
import matplotlib.pyplot as plt
import os
from bit_functions import get_qubit_list

class QuantumOperation:
    def __init__(self):
       self.current_circuit = None
       self.last_result = { 'circuit_Name'  : None,
                            'circuit'       : None,
                            'count'         : None,
                            'time'          : None}
    
    def set_circuit(self, quantum_circuit):
       self.current_circuit = quantum_circuit.copy()
    def get_circuit(self):
       return self.current_circuit

    def get_unitary(self, decimals=3):
        '''Get unitary matrix of current circuit circuit'''
        if self.current_circuit is None:
            return None
        backend = Aer.get_backend('unitary_simulator')
        job = execute(self.current_circuit, backend)
        result = job.result()
        return result.get_unitary(self.current_circuit, decimals)
    
    def get_state_vector(self):
        '''Get state vector of current circuit circuit'''
        if self.current_circuit is None:
            return None
        backend = Aer.get_backend('statevector_simulator')
        job = execute(self.current_circuit, backend)
        result = job.result()
        return result.get_statevector(self.current_circuit)
    
    def get_fake_backend(self, backend_name=None, min_qubit=None, max_qubit = None):
        '''Getting backends based on a few options or the full list or a specific backend name'''
        if not hasattr(self, 'fake_backend'):    
            backend_list = dir(qiskit.providers.fake_provider)
            for backend_name in backend_list:
                try:
                    backend = getattr(qiskit.providers.fake_provider, backend_name)()
                    self.fake_backend.update({ backend_name : {'backend' : backend,'map' : backend.coupling_map, 'qubit' : len({q for couple in backend.coupling_map for q in couple})}})
                except:
                    pass
        if backend_name is None:
            return self.fake_backend
        if max_qubit is not None and min_qubit is not None:
           return {key : value for key, value in self.fake_backend.items() if value['qubit'] <= max_qubit and value['qubit'] >= min_qubit}
        if max_qubit is not None:
           return {key : value for key, value in self.fake_backend.items() if value['qubit'] <= max_qubit}
        if min_qubit is not None:
           return {key : value for key, value in self.fake_backend.items() if value['qubit'] >= min_qubit}
        if backend_name in self.fake_backend:
           return self.fake_backend[backend_name]
        return None

    def run_circuit(self, backend = Aer.get_backend('aer_simulator'), shots = 1024):
        '''Run current quantum circuit with a backend, default is the ideal "aer_simulator".\n
        Returns the simulation results (counts) and the time it took'''
        if self.current_circuit is None:
            return None
        run_qc = self.current_circuit.copy()
        run_qc_qubit = get_qubit_list(run_qc)
        run_qc.add_register(ClassicalRegister(len(run_qc_qubit), 'measure'))
        run_qc.measure(run_qc_qubit, run_qc.clbits)

        result = execute(run_qc, backend = backend,shots=shots).result()
        self.last_result['circuit_Name'] = run_qc.name
        self.last_result['circuit'] = run_qc
        self.last_result['count'] = result.get_counts(run_qc)
        self.last_result['time']  = result.time_taken
        return self.last_result
    
    def get_result_count(self):
        '''get result count'''
        return self.last_result['count']