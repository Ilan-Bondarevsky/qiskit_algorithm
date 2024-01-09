from qiskit import Aer, execute
import qiskit.providers.fake_provider
from qiskit.tools.monitor import job_monitor
from qiskit_ibm_provider import IBMProvider

def run_backend(quantum_circuit, backend, monitor_job = False, *args, **kwargs):
    '''Run current circuit on a given backend'''
    if quantum_circuit is None:
        return None
    job = execute(quantum_circuit, backend=backend, *args, **kwargs)
    if monitor_job:
        job_monitor(job)
    return job

def get_unitary(quantum_circuit, decimals=3, *args, **kwargs):
    '''Get unitary matrix of current circuit'''
    backend = Aer.get_backend('unitary_simulator')
    result = run_backend(quantum_circuit, backend, *args, **kwargs).result()
    return result.get_unitary(quantum_circuit, decimals)

def get_state_vector(quantum_circuit, *args, **kwargs):
    '''Get state vector of current circuit'''
    backend = Aer.get_backend('statevector_simulator')
    result = run_backend(quantum_circuit, backend, *args, **kwargs).result()
    return result.get_statevector(quantum_circuit)

def run_simulator(quantum_circuit, simulator_backend = None, simulator_backend_name='aer_simulator', shots = 1024, *args, **kwargs):
    '''Run circuit on a simulation backend.'''
    if quantum_circuit is None:
        return None
    if simulator_backend is None:
        simulator_backend = Aer.get_backend(simulator_backend_name)
    result = run_backend(quantum_circuit, simulator_backend, shots = shots, *args, **kwargs).result()
    return result

def get_fake_backend_list(min_qubit=None, max_qubit = None):
    '''Get a list of the excisting fake backends provided by qiskit.\n
    Docs: https://docs.quantum.ibm.com/api/qiskit/providers_fake_provider'''
    output = set()
    backend_list = dir(qiskit.providers.fake_provider)
    i = 0
    for backend_name in backend_list:
        try:
            backend = getattr(qiskit.providers.fake_provider, backend_name)()
            num_qubit = len({q for map in backend.coupling_map for q in map})
            if min_qubit is None and max_qubit is None:
                output.add((backend_name, num_qubit))
            else:
                output.add((backend_name, num_qubit)) if min_qubit is not None and num_qubit >= min_qubit else None
                output.add((backend_name, num_qubit)) if max_qubit is not None and num_qubit <= max_qubit else None
        except:
            pass
    return list(output)

def get_fake_backend(name):
    try:
        backend = getattr(qiskit.providers.fake_provider, name)()
        return backend
    except:
        pass

def get_ibm_provider(token, instance="ibm-q/open/main"):
    return IBMProvider(instance=instance, token=token)

def get_ibm_backend_list(provider, **kwargs):
    '''Get backends list of the IBM provider.\n
    Docs: https://qiskit.org/ecosystem/ibm-provider/stubs/qiskit_ibm_provider.IBMProvider.backends.html#qiskit_ibm_provider.IBMProvider.backends'''
    return provider.backends(**kwargs) 

def get_ibm_backend(provider, backend_name='ibm_lagos'):
    '''Choose IBM backend with given backend name'''
    try:
        backend = provider.get_backend(backend_name, hub=None)
    except:
        print('Backend name is not in the IBM library')
    return backend