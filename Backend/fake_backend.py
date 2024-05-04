import qiskit.providers.fake_provider
from qiskit.transpiler import CouplingMap
import qiskit_ibm_runtime.fake_provider
from backend import BACKEND
from qiskit import QuantumCircuit

class FakeBackend(BACKEND):
    def __init__(self, backend_name : str) -> None:
        self.backend = FakeBackend.get_ibm_fake_backend(backend_name=backend_name)
            
    @staticmethod
    def get_ibm_fake_backend_name_list() -> list[str]:
        ibm_dir = dir(qiskit_ibm_runtime.fake_provider)
        return [val for val in ibm_dir if '__' not in val and 'Fake' in val]
    
    @staticmethod
    def get_ibm_fake_backend(backend_name : str):
        try:
            return getattr(qiskit_ibm_runtime.fake_provider, backend_name)()
        except: pass
        fake_backend_name = FakeBackend.get_ibm_fake_backend_name_list()
        for backend in fake_backend_name:
            backend = FakeBackend.get_ibm_fake_backend(backend)
            if backend is not None:
                try:
                    if backend.name == backend_name:
                        return backend
                except: pass
        return None
    
    @staticmethod
    def get_ibm_fake_backend_names_with_limit(min_qubit : int = 1, max_qubit: int = 1500) -> list[str]:
        limited_backend = []
        fake_backend_name = FakeBackend.get_ibm_fake_backend_name_list()
        for backend in fake_backend_name:
            backend = FakeBackend.get_ibm_fake_backend(backend)
            if backend is not None:
                try:
                    num_qubit = backend.num_qubits
                    if num_qubit >= min_qubit and num_qubit <= max_qubit:
                        limited_backend.append(backend.name)
                except: pass
        return limited_backend
    
if __name__ == "__main__":
    print(FakeBackend.get_ibm_fake_backend_name_list())
    
    backend = FakeBackend('fake_auckland')
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