import sys
import os
current_dir = os.getcwd()
sys.path.append(current_dir)
from qiskit import ClassicalRegister
from quantum_circuit import QuantumCircuit

import math

from bit_functions import get_qubit_list

from abc import ABC, abstractmethod

from circuits import cnz, set_value_circuit


class grover_circuit(ABC):
    def __init__(self):
        self.calculation_qc = None
        self.iteration_qc = None
        self.circuit = None
        self.measure_qc = None
    
    @staticmethod
    def oracle(nqubits: int, set_change_value : list=[], mode:str = 'noancilla')->QuantumCircuit:
        '''Building an oracle giving the value of the qubits to go into the oracle.\n
        Each element of the list is a tuple with the index of the qubit and its value = (index, value)'''
        cnz_qc = cnz(nqubits, mode=mode)
        value_qc = set_value_circuit(nqubits, set_change_value, rest_hadamard=False)
        
        qc = QuantumCircuit(cnz_qc.qubits)
        qubits = get_qubit_list(qc)

        qc = qc.compose(value_qc, qubits)
        qc.barrier(qc.qubits)
        qc = qc.compose(cnz_qc, cnz_qc.qubits)
        qc.barrier(qc.qubits)
        qc = qc.compose(value_qc, qubits)
        qc.name = 'Oracle'

        return qc
    
    @staticmethod
    def diffuser(nqubits:int, mode : str='noancilla', show_num_qubits : bool = True) ->QuantumCircuit:
        cnz_cirq = cnz(nqubits, mode)
        qc = QuantumCircuit(cnz_cirq.qubits)
        
        qc.h(get_qubit_list(qc))
        qc.x(get_qubit_list(qc))
        qc.barrier(qc.qubits)
        qc = qc.compose(cnz_cirq, cnz_cirq.qubits)
        qc.barrier(qc.qubits)
        qc.x(get_qubit_list(qc))
        qc.h(get_qubit_list(qc))
        qc.name = f'Diffuser {nqubits}Q' if show_num_qubits else f"Diffuser"

        return qc
    
    def __prep_qubits(self, nqubits : int, prep_value : list = []) -> tuple[QuantumCircuit, int]:
        '''Prepare the qubits value and returns the circuit and the size of the "world", the amount of hadamard gates on the qubits'''
        qc = set_value_circuit(nqubits, qubit_value_list=prep_value, rest_hadamard=True)
        qc.name = 'Prep Qubit'
        return qc, dict(qc.count_ops())['h']
    
    @staticmethod
    def calculate_iterations(qubit_world : int, num_solutions : int = 1) -> None:
        size_N = pow(2, qubit_world)
        if num_solutions is not None and num_solutions:
            if size_N < num_solutions * 2:
                raise Exception("Grover won't work properly! To many solutions!")
            return [math.floor((math.pi * math.sqrt(size_N / num_solutions)) / 4)]
        return list(range(1, math.floor((math.pi * math.sqrt(size_N)) / 4) + 1))

    def create_grover(self, num_solutions : int = 1, prep_value : list = [], iteration_block_diagram : bool = True, prep_block_diagram : bool = False) -> None:
        if self.iteration_qc is None:
            raise Exception("Iteration circuit not found!")
        qubits = get_qubit_list(self.iteration_qc)
        prep_qc, world_qubit_size = self.__prep_qubits(len(qubits), prep_value)
        
        iterations = grover_circuit.calculate_iterations(world_qubit_size, num_solutions)

        qc = self.build_qc_qubit_map()
        qubits = get_qubit_list(qc)
        if prep_block_diagram:
            qc.append(prep_qc, qubits)
        else:
            qc = qc.compose(prep_qc, qubits)  
               
        grover_experiments = []
        for i in iterations:
            if iteration_block_diagram:
                [qc.append(self.iteration_qc, qc.qubits) for _ in range(i)]
            else:
                for _ in range(i):
                    qc = qc.compose(self.iteration_qc, qc.qubits)

            qc.name = f"{self.iteration_qc.name} : Iteration {i}"
            grover_experiments.append(qc)   

        self.circuit = grover_experiments
        self.__add_qubit_measurement()
           
    def __add_qubit_measurement(self) -> None:
        '''
        Measure the qubits of the circuits
        '''
        if self.circuit is None:
            raise Exception("Circuit not found!")
        self.measure_qc = []

        for cur_qc in self.circuit:
            qc = cur_qc.copy()
            qubits = get_qubit_list(qc)

            qc.add_register(ClassicalRegister(len(qubits)))
            qc.measure(qubits, qc.clbits)

            self.measure_qc.append(qc)

    @abstractmethod
    def calculation_logic(self):
        pass
    
    @abstractmethod
    def build_iteration(self):
        pass
    @abstractmethod
    def build_qc_qubit_map(self):
        pass