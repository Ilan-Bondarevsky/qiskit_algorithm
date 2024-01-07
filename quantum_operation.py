from qiskit import Aer, execute
import qiskit.providers.fake_provider

class QuantumOperation:
    def __init__(self, circuit = None):
       self.circuit = circuit
       self.__fakeBackend = set()
    
    def set_circuit(self, quantum_circuit):
       self.circuit = quantum_circuit

    def __run_backend(self, backend_simulator = 'aer_simulator', shots = 1024):
        '''Run current circuit on a given backend'''
        if self.circuit is None:
            return None
        result = execute(self.circuit, backend=Aer.get_backend(backend_simulator), shots = shots).result()
        return result

    def get_unitary(self, decimals=3):
        '''Get unitary matrix of current circuit'''
        result = self.__run_backend('unitary_simulator')
        return result.get_unitary(self.circuit, decimals)
    
    def get_state_vector(self):
        '''Get state vector of current circuit'''
        result = self.__run_backend('statevector_simulator')
        return result.get_statevector(self.circuit)
    
    def run_circuit(self, simulation_backend = 'aer_simulator', shots = 1024):
        '''Run current circuit on a simulation backend.\n
        Note: Need classical bits for measurements for the simulation'''
        if self.circuit is None:
            return None
        if not len(self.circuit.clbits):
            return None
        result = self.__run_backend(simulation_backend, shots = shots)
        return result

    def get_fake_backend(self, backend_name=None, min_qubit=None, max_qubit = None):
        '''Getting backends based on a few options or the full list or a specific backend name'''
        if not len(self.__fakeBackend):
            backend_list = dir(qiskit.providers.fake_provider)
            for backend_name in backend_list:
                try:
                    backend = getattr(qiskit.providers.fake_provider, backend_name)()
                    self.__fakeBackend.update({ backend_name : {'backend' : backend,'map' : backend.coupling_map, 'qubit' : len({q for couple in backend.coupling_map for q in couple})}})
                except:
                    pass

        #if not hasattr(self, 'fake_backend'):    
        #    backend_list = dir(qiskit.providers.fake_provider)
        #    for backend_name in backend_list:
        #        try:
        #            backend = getattr(qiskit.providers.fake_provider, backend_name)()
        #            self.fake_backend.update({ backend_name : {'backend' : backend,'map' : backend.coupling_map, 'qubit' : len({q for couple in backend.coupling_map for q in couple})}})
        #        except:
        #            pass
        
        if max_qubit is not None and min_qubit is not None:
           return {key : value for key, value in self.__fakeBackend.items() if value['qubit'] <= max_qubit and value['qubit'] >= min_qubit}
        if max_qubit is not None:
           return {key : value for key, value in self.__fakeBackend.items() if value['qubit'] <= max_qubit}
        if min_qubit is not None:
           return {key : value for key, value in self.__fakeBackend.items() if value['qubit'] >= min_qubit}
        if backend_name is None:
            return self.__fakeBackend
        if backend_name in self.__fakeBackend:
           return self.__fakeBackend[backend_name]
        return None