# from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister
import sys
import os
current_dir = os.getcwd()
sys.path.append(current_dir)
from Result.result import *
from qiskit.quantum_info import Operator
from quantum_circuit import QuantumCircuit
import math
from qiskit.circuit import instruction
from typing import NamedTuple
import numpy as np
from qiskit import QuantumRegister, AncillaRegister


class DepthCalc:
    def __init__(self, qc : QuantumCircuit) -> None:
        self.__depth_dict = {}
        self.__qc = qc
        
        self.__count_gate()
    
    def __count_gate(self) -> None:
        for instruction in self.__qc.data:
            if instruction.operation.name.lower() == 'barrier':
                continue
            num_qubits_in_inst = len(instruction.qubits)
            if num_qubits_in_inst not in self.__depth_dict:
                self.__depth_dict[num_qubits_in_inst] = {'NumGates' : 0}
            
            add_gate = True
            for qubit in instruction.qubits:
                if qubit not in self.__depth_dict[num_qubits_in_inst]:
                    self.__depth_dict[num_qubits_in_inst][qubit] = 0
                self.__depth_dict[num_qubits_in_inst][qubit] = self.__depth_dict[num_qubits_in_inst][qubit] + 1
                if add_gate:
                    add_gate = False
                    self.__depth_dict[num_qubits_in_inst]['NumGates'] = self.__depth_dict[num_qubits_in_inst]['NumGates'] + 1
                    
    def get_num_gates(self, qubit_gate_num : int = 1) -> int:
        return self.__depth_dict[qubit_gate_num]['NumGates']
    
    def get_max_qubit_gate(self, qubit_gate_num : int | None = None):
        qubit_count_dict = {}
        for gate_num in self.__depth_dict:
            if qubit_gate_num is not None and gate_num != qubit_gate_num:
                continue    
            for qubit, count in self.__depth_dict[gate_num].items():
                if qubit == 'NumGates':
                    continue
                if qubit not in qubit_count_dict:
                    qubit_count_dict[qubit] = 0
                qubit_count_dict[qubit] = qubit_count_dict[qubit] + count
        return max(qubit_count_dict, key=qubit_count_dict.get)

if __name__ == '__main__':
    qc = QuantumCircuit(QuantumRegister(5))
    qc.add_register(AncillaRegister(4))
    qc.h(0)
    qc.x(2)
    qc.cx(3, 5)
    qc.ccx(1,3,6)
    qc.h(0)
    qc.x(3)
    qc.h(2)
    qc.h(2)
    qc.x(4)
    qc.x(3)
    qc.h(0)
    qc.x(0)
    qc.x(0)
    qc.barrier(1,2,3,4)
    qc.cx(0,1)
    qc.x(0)
    qc.x(0)
    qc.cx(0,1)
    qc.h(0)
    y=DepthCalc(qc)
    print(y.get_max_qubit_gate(3))
    print(y.get_num_gates(1))
    