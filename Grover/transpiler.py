# from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister
import sys
sys.path.append('')
from Backend.backend import *
from Result.result import *
from qiskit.quantum_info import Operator
from quantum_circuit import QuantumCircuit

from qiskit.circuit import instruction
from typing import NamedTuple
class QuantumInstruction(NamedTuple):
    qubits : list[int]
    name : str
class IndexInstruction(NamedTuple):
    q_instruction : QuantumInstruction
    index: int
    
qc = QuantumCircuit(4)
  
qc.x(0)
qc.x(1)
qc.cx(1,0)
qc.h(0)
qc.h(0)
qc.h(0)
qc.cx(0,1)
qc.cx(0,1)
qc.cx(1,0)
qc.h(3)
qc.x(3)
qc.h(3)
qc.x(3)
qc.x(3)
qc.u(0,1,0,1)

def remove_similiar_adjacent(qc : QuantumCircuit):
    removed_instruction = False
    instruction_index = 0
    instruction_dict : dict[IndexInstruction] = {}
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

def minimize_qubit_gates(qc : QuantumCircuit) -> QuantumCircuit | None:
    if len(qc.qubits) != 1:
        return None
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
    
    

# print("Insturctions:")
# for x, y in enumerate(qc.data):
#     print(f"Inst {x} : {y}")
# print(qc)
# print(get_inst_index_dict(qc))

# qc, x = remove_similiar_adjacent(qc)
# # print(qc)
# qc = unite_qubit_gates(qc)
qc = QuantumCircuit(1)
qc.x(0)
qc.h(0)
qc.x(0)

print("HIHIHI")
print(qc.get_unitary_matrix())
print(qc.get_density_matrix())
print(qc.get_state_vector())
print(qc.get_stabilizer_state())
# minimize_qubit_gates(qc)
# print(qc)
# print(qc)
