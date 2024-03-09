from qiskit import Aer, execute, transpile
import qiskit.providers.fake_provider
from qiskit_ibm_provider import IBMProvider
from qiskit.transpiler.passes import RemoveBarriers
from qiskit_aer import AerSimulator

def run_backend(quantum_circuit, backend, *args, **kwargs):
    '''Run current circuit on a given backend'''
    if quantum_circuit is None:
        return None
    job = execute(quantum_circuit, backend=backend, *args, **kwargs)
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

def run_simulator(quantum_circuit, simulator_backend = None, shots = 1024, *args, **kwargs):
    '''Run circuit on a simulation backend.'''
    if quantum_circuit is None:
        return None
    if simulator_backend is None:
        simulator_backend = AerSimulator()
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
            elif max_qubit is None:
                output.add((backend_name, num_qubit)) if num_qubit >= min_qubit else None
            elif min_qubit is None:
                output.add((backend_name, num_qubit)) if num_qubit <= max_qubit else None
            else:
                output.add((backend_name, num_qubit)) if num_qubit >= min_qubit and num_qubit <= max_qubit else None
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

def transpile_quantum_circuit(qc, backend_name="Aer", optimization_level=0, initial_layout = None):
    backend = get_fake_backend(backend_name)
    if backend is None:
        backend = AerSimulator()
    if initial_layout == 'Full_Range':
        initial_layout = list(range(len(qc.qubits)))

    removed_barriar_qc = RemoveBarriers()(qc)
    
    transpiled_qc = transpile(circuits=removed_barriar_qc, backend=backend,optimization_level=optimization_level, initial_layout=initial_layout)
    return transpiled_qc

def get_transpiled_circuits_of_circuit(qc, backend_name_list:list = ['Aer'], initial_layout_list:list = [None], optimization_level_list:list = [0]):
    output_list = []
    for backend in backend_name_list:
        for layout in initial_layout_list :
            for level in optimization_level_list:
                output_list.append(transpile_quantum_circuit(qc, backend_name=backend, initial_layout=layout,optimization_level=level))
                output_list[-1].name = f"{backend} | {layout} | {level}" 
    return output_list