# from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister
import sys
import os
current_dir = os.getcwd()
sys.path.append(current_dir)
from Backend.backend import *
from Result.result import *
from qiskit.quantum_info import Operator
from quantum_circuit import QuantumCircuit
import math
from qiskit.circuit import instruction
from typing import NamedTuple
import numpy as np
from Grover.grover_num_list_cirq import find_num_list
from qiskit import QuantumRegister, AncillaRegister

class QuantumInstruction(NamedTuple):
    qubits : list[int]
    name : str
class IndexInstruction(NamedTuple):
    q_instruction : QuantumInstruction
    index: int

def contiguous_sublists(input_list : list):
    length = len(input_list)
    sublists = []
    # Generate all contiguous sublists
    for start in range(length):
        for end in range(start + 1, length + 1):
            sublists.append(input_list[start:end])
    # Sort the sublists by length in descending order
    sublists.sort(key=len, reverse=True)
    return sublists

class our_tranpiler:
    def __init__(self, qc : QuantumCircuit) -> None:
        self.qc = qc
        self.remove_barriar_gate()
        self.remove_similiar_adjacent()
    
    def get_circuit(self) ->QuantumCircuit:
        return self.qc
    
    def remove_barriar_gate(self):
        valid_instruction_list = []
        for instruction in self.qc.data:
            if instruction.operation.name.lower() != 'barrier':
                valid_instruction_list.append(instruction)
        self.qc.data = valid_instruction_list

    def remove_similiar_adjacent(self):
        qubit_dict = { qubit : [] for qubit in self.qc.qubits}
        valid_results = []
        # Step 1 : Run on each instruction
        for instruction in self.qc.data:
            valid_instruction = False
            # Step 2 : Check if last accurance for qubits happened (For all qubits)
            for qubit in instruction.qubits:
                if len(qubit_dict[qubit]) > 0:                    
                    if instruction != qubit_dict[qubit][-1]:
                        valid_instruction = True
                else:
                    valid_instruction = True
            # Step 3 : Update for all qubits list the instruction
            for qubit in instruction.qubits:
                if valid_instruction:
                    qubit_dict[qubit].append(instruction)
                else:
                    qubit_dict[qubit].pop()
            # Step 4 : Save valid instruction or remove instruction if not valid from list    
            if valid_instruction:
                valid_results.append(instruction)
            else:
                for index, inst in enumerate(valid_results[::-1]):
                    index = len(valid_results) - index - 1
                    if inst == instruction:
                        valid_results.pop(index)
                        break
        # Step 5 : Save new instruction list to the coircuit data
        self.qc.data = valid_results
        
    def unify_one_qubit_instructions(self, instruction_list : list) -> None | list:
        # Step 1 : Check all instruction are one qubit and the same qubit
        qubit = None
        for instruction in instruction_list:
            if len(instruction.qubits) > 1:
                return None
            if qubit is None:
                qubit = instruction.qubits[0]
            elif qubit != instruction.qubits[0]:
                return None
        
        for length in range(len(instruction_list) - 1, 1, -1):
            for start_index in range(len(instruction_list)):
                if start_index + length >= len(instruction_list):
                    continue
                instruction_sublist = instruction_list[start_index : length + 1]
                
                qc = QuantumCircuit(qubit)
                qc.data = instruction_sublist
                
  
        
def remove_barriar_gate(qc:  QuantumCircuit):
    instruction_index = 0
    while len(qc.data) > instruction_index:
        cur_inst = qc.data[instruction_index]
        if cur_inst.operation.name.lower() == 'barrier':
            del qc.data[instruction_index]
        else:
            instruction_index = instruction_index + 1
    return qc

def remove_similiar_adjacent(qc : QuantumCircuit):
    removed_instruction = False
    instruction_index = 0
    instruction_dict : dict[IndexInstruction] = {}
    for k in qc.data:
        print(k)
    
    for index, instruction in enumerate(qc.data):
        for qubit in instruction.qubits:
            if qubit._index not in instruction_dict:
                instruction_dict[qubit._index] = []
            instruction_dict[qubit._index].append()
            
        print(instruction.operation.name)
        
        print(instruction.qubits)
        print(instruction.qubits[0]._index)
        pass
    while len(qc.data) > instruction_index:
        prev_index = None
        index_increment = 1
        inst_qubits = [qubit._index for qubit in qc.data[instruction_index].qubits]
        remove_instruction_count = 0
        # Check if previous instruction is the same as current instruction for each qubit
        for qubit_index in inst_qubits:
            if qubit_index in instruction_dict:
                prev_inst = qc.data[instruction_dict[qubit_index][-1]]
                cur_inst = qc.data[instruction_index]
                if cur_inst == prev_inst:
                    remove_instruction_count = remove_instruction_count + 1
        for qubit_index in inst_qubits:
            # Pop from dict previous instruction index
            if len(inst_qubits) == remove_instruction_count:
                index_increment, removed_instruction, prev_index = (-1, True, instruction_dict[qubit_index].pop())
            # Add new instruction to dict
            elif qubit_index in instruction_dict:
                instruction_dict[qubit_index].append(instruction_index)
            else:
                instruction_dict[qubit_index] = [instruction_index]      
        # Remove instructions (current and previous) if needed
        if prev_index is not None:
            del qc.data[instruction_index]
            del qc.data[prev_index]
        instruction_index = instruction_index + index_increment
    return qc, removed_instruction

def unite_qubit_gates(qc : QuantumCircuit):
    inst_dict = get_inst_index_dict(qc)
    print("Start")
    print(qc)
    print(inst_dict)
    for x,y in enumerate(qc.data):
        print(f"Indexx{x} : {y}")
    for qubit in inst_dict:
        qubit_inst_list = [qc.data[index] for index in inst_dict[qubit]]
        start_index, end_index = (0, 0)
        print(f"Qubit {qubit}")
        while start_index < len(qubit_inst_list):
            print("Circuit")
            while end_index < len(qubit_inst_list) and len(qubit_inst_list[end_index].qubits) == 1: end_index = end_index + 1
            cur_inst = qubit_inst_list[start_index:end_index]
            cur_qc = create_circuit_from_instructions(cur_inst)
            print(cur_qc)
            start_index, end_index = (end_index + 1, end_index + 1)
    return qc
            
def create_circuit_from_instructions(inst_list : list, qc : QuantumCircuit = None) -> QuantumCircuit:
    '''Create a Quantum Circuit based on an instruction list
    : param inst_list = Instruction List or list of INTEGER, each one is an instruction index from given qc
    : param qc = If None, build with the inst_list, else get instruction from qc using inst_list
    : Note = Working only on 1 qubit instructions ONLY and for KNOWN GATES ONLY'''
    if qc is not None:
        inst_list = [qc.data[index] for index in inst_list]
    qc = QuantumCircuit(1)
    for instruction in inst_list:
        gate_name = instruction.operation.name
        gate_params = list(instruction.operation.params)
        gate_params.append(0)
        getattr(qc, gate_name)(*gate_params)
    return qc

def minimize_one_qubit_circuit(qc : QuantumCircuit) -> QuantumCircuit | None:
    if len(qc.qubits) != 1:
        return None
    if len(qc.data) <= 1:
        return qc
    
    unitary_matrix = qc.get_unitary_matrix()
    
    
    x = Operator(qc).data
    y = x[0]
    z = x[1]
    
    w = y[0]
    m = y[1]
    print(w)
    print(type(w))
    print(w.real)
    print(w.imag)
    
    # qc.measure_all()
    # print(qc)
    # y = x.execute(qc)
    # z = ResultData(y)
    # print(z.get_unitary(qc))
    # print(z.get_counts(qc))
    # qc = x.traspile_qiskit(qc)
    # print('hi')
    # result = x.execute(qc)
    # print(result)
    # result = ResultData(BACKEND().execute(qc))
    # print(result.get_counts())
    # unitary = result.get_unitary(qc)
    
def get_inst_index_dict(qc : QuantumCircuit) -> dict[int, list[int]]:
    inst_index_dict = {}
    for index, instruction in enumerate(qc.data):
        inst_qubits = [qubit._index for qubit in instruction.qubits]
        for qubit in inst_qubits:
            if qubit in inst_index_dict:
                inst_index_dict[qubit].append(index)
            else:
                inst_index_dict[qubit] = [index]
    return inst_index_dict  

def check_u3_gate(qc : QuantumCircuit):
    unitary_matrix = qc.get_unitary_matrix()
    
def get_theta(qc : QuantumCircuit):
    unitary_matrix = qc.get_unitary_matrix()
    print(unitary_matrix)
    top_left = unitary_matrix[0][0]
    imag = top_left.imag
    real = top_left.real
    if imag:
        return None
    return round(normalize_angle(2 * math.acos(real)), 4)


def get_angle(matrix_value : float, value_divisor : float = 1) -> list[float]:
    if value_divisor == 0:
        return [0]
    real_calc_value = round(np.real(matrix_value) / value_divisor, 4)
    img_calc_value = round(np.imag(matrix_value) / value_divisor, 4)

    real_degree = math.acos(real_calc_value)
    img_degree = math.asin(img_calc_value)
    
    check_real = round(math.sin(real_degree), 4)
    check_img = round(math.cos(img_degree), 4)
    
    real_calc_value = round(np.real(matrix_value) / value_divisor, 4)
    img_calc_value = round(np.imag(matrix_value) / value_divisor, 4)
    
    if abs(check_real) == abs(img_calc_value) and abs(check_img) == abs(real_calc_value):
        return [normalize_angle(round(img_degree,4)), normalize_angle(round(real_degree,4))]
    return []


def check_sum_angles_value(qc : QuantumCircuit, theta_val : float, phi_val: list[float] = [], lambda_val : list[float] = []) -> list[float]:
    if theta_val is None or (len(phi_val) == 0 and len(lambda_val) == 0):
        return []
    unitary_matrix = qc.get_unitary_matrix()
    matrix_value = unitary_matrix[1][1] # Bottom Right
    cos_theta = math.cos(theta_val / 2)
    if len(phi_val) and len(lambda_val):
        for p in phi_val:
            for l in lambda_val:
                if round(np.real(matrix_value), 4) == round(cos_theta * math.cos(p + l), 4) and round(np.imag(matrix_value), 4) == round(cos_theta * math.sin(p + l), 4):
                    return [p, l]
    else:
        pass
    return []

def check_bottom_left_value(qc : QuantumCircuit, theta_value : float, phi_value : list[float] | float, lambda_val : list[float] | float) -> tuple[float,float] | None:
    if phi_value is None or lambda_val is None or theta_value is None:
        return None, None
    if not isinstance(phi_value, list):
        phi_value = [phi_value]
    if not isinstance(lambda_val, list):
        lambda_val = [lambda_val]
    unitary_matrix = qc.get_unitary_matrix()
    matrix_value = unitary_matrix[1][1] # Bottom Right
    cos_theta = round(math.cos(theta_value / 2), 4)
    if cos_theta == 0:
        return phi_value[0], lambda_val[0]
    
    for p in phi_value:
        for l in lambda_val:
            cos_sum = round(math.cos(p + l), 4)
            sin_sum = round(math.sin(p + l), 4)
            if round(np.imag(matrix_value), 4) == round(cos_theta * sin_sum, 4) and round(np.real(matrix_value), 4) == round(cos_theta * cos_sum, 4):
                return normalize_angle(p) ,normalize_angle(l)
    return None, None 

def get_unitary_angles(qc : QuantumCircuit) -> list[float]:
    theta = get_theta(qc)
    if theta is None:
        return []
    unitary_matrix = qc.get_unitary_matrix()
    
    phi_angles = get_angle(unitary_matrix[1][0], round(math.sin(theta / 2), 4))
    lambda_angles = get_angle(-unitary_matrix[0][1], round(math.sin(theta / 2), 4))
    if len(phi_angles) == 0 and len(lambda_angles) == 0:
        return []
    elif len(phi_angles) == 2 and len(lambda_angles) == 2:
        cos_theta = round(math.cos(theta / 2), 4)
        for p in phi_angles:
            for l in lambda_angles:
                cos_sum = round(math.cos(p + l), 4)
                sin_sum = round(math.sin(p + l), 4)
                if round(np.imag(unitary_matrix[1][1]), 4) == round(cos_theta * sin_sum, 4) and round(np.real(unitary_matrix[1][1]), 4) == round(cos_theta * cos_sum, 4):
                    return [theta, normalize_angle(p) ,normalize_angle(l)]
    else:
        lambda_angles = get_angle(unitary_matrix[1][1], round(math.cos(theta / 2), 4))
        if len(lambda_angles):
            for p in phi_angles:
                for l in lambda_angles:
                    if p == l:
                        continue
                    return [theta, p, l]
            return [theta, p, l]
        return []
    return []

def normalize_angle(angle : float):
    angle = angle % ( 2 * math.pi)
    if angle >= math.pi:
        return angle - 2 *math.pi
    return angle
    # return (angle + math.pi) % (2 * math.pi) - math.pi  

if __name__ == '__main__':
    
    # print("Insturctions:")
    # for x, y in enumerate(qc.data):
    #     print(f"Inst {x} : {y}")
    # print(qc)
    # print(get_inst_index_dict(qc))

    # qc, x = remove_similiar_adjacent(qc)
    # # print(qc)
    # qc = unite_qubit_gates(qc)
    # qc = QuantumCircuit(1)
    # qc.h(0)

    # theta_val = get_theta(qc)
    # lambda_val_1 = get_lambda(qc, theta_val)
    # phi_val_1 = get_phi_with_lambda(qc, theta_val, lambda_val_1)
    # phi_val_2 = get_phi(qc, theta_val)
    # lambda_val_2 = get_phi_with_lambda(qc, theta_val, phi_val_2)
    # print(f"Theta = {theta_val}")
    # print(f"Phi = {phi_val_1} , {phi_val_2}")
    # print(f"Lambda = {lambda_val_1}, {lambda_val_2}")

    # a = 1 / math.sqrt(2)
    # b = 1 / math.sqrt(2)
    # c = 1 / math.sqrt(2)
    # d = -math.sqrt(2) / math.sqrt(2)
    # qc = QuantumCircuit(1)
    # qc.h(0)
    # qc.x(0)
    # print(f"{a} , {b} , {c} , {d}")

    # # theta = 2 * math.acos(a)
    # # print(theta)
    # print(get_unitary_angles(qc))
    
    # theta = get_theta(qc)
    # print(theta)
    # x = get_unitary_angle(qc, theta, True)
    # print(x)
    # print('bye')
    # # print(theta)
    # # print("continue")

    # x= round(-np.real(b) / math.sin(theta / 2),4)
    # y =  round(-np.imag(b) / math.sin(theta / 2),4)
    # e = round(math.acos(x),4)
    # e2 = round(math.asin(y),4)

    # print(x)
    # print(y)
    # print('\n')
    # print(e)
    # print(e2)
    # print('\n')
    # z = round(math.cos(e),4)
    # z2 = round(math.sin(e2),4)
    # print(z)
    # print(z2)
    # print('\n')
    # print(abs(z) == abs(x))
    # print(z2==y)
    # x =  find_num_list()
    # x.build_iteration(winner_list=[5],num_array = [0,5,3], block_diagram=False)
    # x.create_grover(num_solutions=1,block_diagram=False)
    # print(x.measure_qc[0].draw())
    
    # qc = remove_barriar_gate(x.measure_qc[0])
    # print(qc.draw())
    
    # qc, is_removed = remove_similiar_adjacent(qc)
    # print(qc.draw())
    
    
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
    print(qc.draw())
    x = our_tranpiler(qc)
    print(x.get_circuit().draw())