from qiskit.transpiler import CouplingMap
from backend import BACKEND
from qiskit_ibm_provider import IBMProvider

class IBM_backend(BACKEND):
    def __init__(self, api_token : str = '', save_token_locally : bool = False) -> None:
        if save_token_locally:
            IBMProvider.save_account(token=api_token)
            self.provider = IBMProvider()
        else:
            self.provider = IBMProvider(token=api_token)
        self.backend = self.provider.get_backend('ibmq_qasm_simulator')
    
    def get_operational_backend_list(self):
        return self.provider.backends(simulator=False, operational=True)
    
    def get_backend_min_qubit(self, min_qubit : int):
        return self.provider.backends(min_num_qubits=min_qubit)
    
    def set_ibm_backend(self, ibm_backend= 'ibmq_qasm_simulator'):
        if isinstance(ibm_backend, str):
            self.backend = self.provider.get_backend(ibm_backend)
        else:
            self.backend = ibm_backend

        
    