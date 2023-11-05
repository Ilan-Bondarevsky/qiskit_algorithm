from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister
from quantum_cirq_func import QuantumCircuitFunction, get_qubit_list, cnz
import math

class Grover(QuantumCircuitFunction):
    def __init__(self, prep_func, oracle_func, iteration_func, data_func = None):
        super().__init__()
        self.functions = {'prep' : prep_func,
                          'data' : data_func,
                          'oracle' : oracle_func,
                          'iteration' : iteration_func}
        self.iterations = None
    
    def create_diffuser(self, mode = 'noancilla'):
        if 'iteration' not in self.circuit and self.circuit['iteration'] is None:
            return False
        qubits_list = get_qubit_list(self.circuit['iteration'])

        qc = QuantumCircuit(QuantumRegister(len(qubits_list), 'dif_q'))
        qc.barrier(qc.qubits)
        qc.h(qc.qubits)
        qc.x(qc.qubits)

        z_circuit = cnz(len(qubits_list), mode)
        qc.add_register(AncillaRegister(z_circuit.num_ancillas, 'dif_anc'))
        qc.barrier(qc.qubits)
        qc = qc.compose(z_circuit, qubits=list(range(qc.num_qubits)))
        qc.barrier(qc.qubits)

        qc.x(filter(lambda q : q not in qc.ancillas, qc.qubits))
        qc.h(filter(lambda q : q not in qc.ancillas, qc.qubits))
        qc.barrier(qc.qubits)
        qc.name='diffuser'
        self.circuit['diffuser'] = qc

        self.circuit['iteration'].add_register(qc.ancillas)
        self.circuit['iteration'] = self.circuit['iteration'].compose(qc, qubits_list[:] + qc.ancillas[:])
        return True
    
    def create_oracle(self,mode ='noancilla', *args, **kwargs):
        try:
            self.circuit['oracle'] = self.functions['oracle'](mode=mode, *args, **kwargs)
            return True
        except Exception as e:
            print(e)
            self.circuit['oracle'] = None
            return False

    def create_data(self, mode ='noancilla', *args, **kwargs):
        try:
            self.circuit['data'] = self.functions['data'](mode=mode,*args, **kwargs)
            return True
        except Exception as e:
            print(e)
            self.circuit['data'] = None
            return False
            
    def create_prep(self, mode ='noancilla', *args, **kwargs):
        try:
            self.circuit['prep'] = self.functions['prep'](mode = mode, *args, **kwargs)
            return True
        except:
            self.circuit['prep'] = None
            return False


    def create_iteration(self, mode='noancilla'):
        try:
            self.circuit['iteration'] = self.functions['iteration'](oracle = self.circuit['oracle'], data = self.circuit['data'])
            self.create_diffuser(mode = mode)
            return True
        except Exception as e:
            print(e)
            self.circuit['iteration'] = None
            return False

    def calculate_iterations(self, space_size, answers = 1):
        self.iterations = math.floor((math.pi * math.sqrt(space_size / answers)) / 4)

    def create_full_grover(self, answers = 1, space_size=None):
        if 'iteration' not in self.circuit or self.circuit['iteration'] is None:
            return False
        qc = self.circuit['iteration'].copy()
        self.circuit['full'] = QuantumCircuit(qc.qubits)

        qubits_list = get_qubit_list(qc)
        space_size = pow(2, len(qubits_list)) if space_size is None else space_size
        if self.iterations is None:
            self.calculate_iterations(space_size, answers)

        for _ in range(self.iterations):
            self.circuit['full'].barrier(qc.qubits)
            self.circuit['full'] = self.circuit['full'].compose(qc, qc.qubits)

        self.circuit['prep'] = self.functions['prep'](len(qubits_list))
        if self.circuit['prep'] is None:
            return False
        
        qc = self.circuit['prep'].copy()
        qubits_list = get_qubit_list(qc)
        qc.add_register(self.circuit['full'].ancillas)
        self.circuit['full'] = qc.compose(self.circuit['full'], qubits_list[:] + self.circuit['full'].ancillas[:])
        self.circuit['full'].name ='Grover Full Circuit'
        return True