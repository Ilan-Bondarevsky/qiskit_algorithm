from qiskit import execute, ClassicalRegister
from qiskit.tools.visualization import plot_histogram
import matplotlib.pyplot as plt
import os
from qiskit_ibm_provider import IBMProvider
from qiskit.tools.monitor import job_monitor
from bit_functions import get_qubit_list

class IBMOperation():
    def __init__(self, token, instance="ibm-q/open/main"):
        self.provider = IBMProvider(instance=instance, token=token)
        self.backend = None
        self.current_circuit = None
        self.last_result = {'circuit_Name'  : None,
                            'circuit'       : None,
                            'count'         : None,
                            'time'          : None,
                            'id'            : None}
  
    def set_circuit(self, quantum_circuit):
       self.current_circuit = quantum_circuit.copy()
    def get_circuit(self):
       return self.current_circuit

    def get_backends(self, **kwargs):
        '''Get a list of the backends of the IBM provider.\n
        Can see options: https://qiskit.org/ecosystem/ibm-provider/stubs/qiskit_ibm_provider.IBMProvider.backends.html#qiskit_ibm_provider.IBMProvider.backends''' 
        return self.provider.backends(**kwargs)

    def choose_backend(self, backend_name='ibm_lagos'):
        '''Choose IBM backend with given backend name'''
        try:
            self.backend = self.provider.get_backend(backend_name, hub=None)
        except:
            print('Backend name is not in the IBM library')

    def run_circuit(self, shots=1024):
        '''Run circuit on IBM hardware multiple times (shots)'''
        run_qc = self.current_circuit.copy()
        run_qc_qubit = get_qubit_list(run_qc)
        run_qc.add_register(ClassicalRegister(len(run_qc_qubit), 'measure'))
        run_qc.measure(run_qc_qubit, run_qc.clbits)

        job = execute(run_qc, backend=self.backend, shots=shots)
        self.last_result['id'] = job.job_id()
        job_monitor(job)
        
        result = job.result()
        self.last_result['circuit_Name'] = run_qc.name
        self.last_result['circuit'] = run_qc
        self.last_result['count'] = result.get_counts(run_qc)
        self.last_result['time'] = result.time_taken
        return self.last_result

    def get_result_count(self):
        '''Returns result count'''
        return self.last_result['count']
    
    def draw_circuit(self, save_cirq, image_type='mpl', file_directory = None):
       '''Draw the last circuit.\n
       Can save in directory'''
       if self.current_circuit is None:
            return None
       (self.current_circuit.draw(image_type)).show()
       if save_cirq:
            plt.savefig(os.path.join(
                file_directory if file_directory is not None else ''
                ,''.join([self.current_circuit.name] + ['_draw.png'])))
    
