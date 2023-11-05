from qiskit import Aer, execute
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, AncillaRegister
import qiskit.providers.fake_provider
from qiskit.tools.visualization import plot_histogram
import matplotlib.pyplot as plt
import os
from qiskit_ibm_provider import IBMProvider
from qiskit.tools.monitor import job_monitor

def create_h_prep(num_qubit):
      '''Returns a circuit with H gate on allt he qubits'''
      qc = QuantumCircuit(QuantumRegister(num_qubit))
      qc.h(qc.qubits)
      return qc

def get_qubit_list(qc):
    '''Get a list of the qubits without the ancillas'''
    return list(filter(lambda q : q not in qc.ancillas, qc.qubits))

def cnz(qubits, mode = 'noancilla'):
  '''Craete a contorl not Z (cnz) circuit based on the number of qubits'''
  qc = QuantumCircuit(QuantumRegister(qubits, 'qubit'))
  if qubits < 1:
    return None
  elif qubits == 1:
    qc.z(qubits-1)
  elif qubits == 2:
    qc.cz(qubits-2, qubits-1)
  else:
    if mode == 'noancilla':
      qc.h(qubits-1)
      qc.mcx(list(range(qubits-1)), qubits-1)
      qc.h(qubits-1)
    else:
      ancilla = qubits - 2
      qc.add_register(AncillaRegister(ancilla, 'ancilla'))
      mid_q = (ancilla + qubits) // 2 - 1
      for i in range(ancilla):
        qc.ccx(mid_q - i, mid_q + i + 1, mid_q + i + 2)

      qc.cz(0, qubits + ancilla - 1)

      for i in list(range(ancilla))[::-1]:
        qc.ccx(mid_q - i, mid_q + i + 1, mid_q + i + 2)
  qc.name = "cnz " + str(qubits)
  return qc

class QuantumCircuitFunction():
    def __init__(self):
       self.circuit = {}
       self.result = {'circuit' : None,
                      'count' : None,
                      'time' : None}
    def get_unitary(self, qc_name, decimals=3):
        '''Get unitary matrix of a circuit'''
        if qc_name not in self.circuit:
           return None
        run_qc = self.circuit[qc_name].copy()
        
        backend = Aer.get_backend('unitary_simulator')
        job = execute(run_qc, backend)
        result = job.result()
        return result.get_unitary(run_qc, decimals)
    
    def get_fake_backend(self, backend_name=None, min_qubit=None, max_qubit = None):
        '''Getting backends based on a few options or the full list or a specific backend name'''
        if not hasattr(self, 'fake_backend'):    
            backend_list = dir(qiskit.providers.fake_provider)
            for backend_name in backend_list:
                try:
                    backend = getattr(qiskit.providers.fake_provider, backend_name)()
                    self.fake_backend.update({ backend_name : {'backend' : backend,'map' : backend.coupling_map, 'qubit' : len({q for couple in backend.coupling_map for q in couple})}})
                except:
                    pass
        if backend_name is None:
            return self.fake_backend
        if max_qubit is not None and min_qubit is not None:
           return {key : value for key, value in self.fake_backend.items() if value['qubit'] <= max_qubit and value['qubit'] >= min_qubit}
        if max_qubit is not None:
           return {key : value for key, value in self.fake_backend.items() if value['qubit'] <= max_qubit}
        if min_qubit is not None:
           return {key : value for key, value in self.fake_backend.items() if value['qubit'] >= min_qubit}
        if backend_name in self.fake_backend:
           return self.fake_backend[backend_name]
        return None

    def run_circuit(self, qc_name, backend = Aer.get_backend('aer_simulator'), shots = 1024):
        '''Run quantum circuit by name with given backend, default is the ideal "aer_simulator".
        Returns the simulation results (counts) and the time it took'''
        if qc_name not in self.circuit:
           return None
        run_qc = self.circuit[qc_name].copy()
        run_qc_qubit = get_qubit_list(run_qc)
        run_qc.add_register(ClassicalRegister(len(run_qc_qubit), 'measure'))
        run_qc.measure(run_qc_qubit, run_qc.clbits)

        result = execute(run_qc, backend = backend,shots=shots).result()
        self.result['circuit'] = run_qc.name
        self.result['count'] = result.get_counts(run_qc)
        self.result['time']  = result.time_taken
        return self.result['time']
    
    def draw_histogram(self, file_directory=None,plot_title = None):
       '''Saving a PNG image of the histogram drawing of the last circuit'''
       if file_directory is None:
          file_directory = ''
       if self.result['count'] is None:
          return None
       if plot_title is None:
          plot_title = self.result['circuit']
       plot_histogram(self.result['count'], title=plot_title).show()
       plt.savefig(os.path.join(file_directory,'histogram.png'))
    
    def draw_circuit(self, qc_name, image_type=None, file_directory = None):
       '''Draw circuit'''
       if qc_name not in self.circuit:
          return None
       if file_directory is None:
          file_directory = ''
       if image_type is None:
          print(self.circuit[qc_name].draw())
       elif image_type == 'mpl':
          (self.circuit[qc_name].draw(image_type)).show()
          plt.savefig(os.path.join(file_directory,''.join([qc_name] + ['_draw.png']))) 

    def get_circuits(self):
       return self.circuit
    
class IBM_run():
  def __init__(self, token, instance="ibm-q/open/main"):
    self.provider = IBMProvider(instance=instance, token=token)
    self.backend = None
    self.result = {
       'circuit' : None,
       'count' : None,
       'time' : None,
       'id' : None
    }
  
  def get_backends(self, **kwargs):
    '''Get a list of the backends of the IBM provider.
    Can see options: https://qiskit.org/ecosystem/ibm-provider/stubs/qiskit_ibm_provider.IBMProvider.backends.html#qiskit_ibm_provider.IBMProvider.backends''' 
    return self.provider.backends(**kwargs)
  
  def choose_backend(self, backend_name='ibm_lagos'):
    '''Choose bIBM backend with given backend name'''
    try:
      self.backend = self.provider.get_backend(backend_name, hub=None)
    except:
       print('Backend name is not in the IBM library')

  def run_circuit(self, qc, shots=1024):
    '''Run circuit on IBM hardware multiple times (shots)'''
    job = execute(qc, backend=self.backend, shots=shots)
    self.result['id'] = job.job_id()
    job_monitor(job)
    result = job.result()
    self.result['circuit'] = qc.name
    self.result['count'] = result.get_counts(qc)
    self.result['time'] = result.time_taken
    
  def draw_histogram(self, file_directory='',plot_title = None):
       '''Saving a PNG image of the histogram drawing of the last circuit'''
       if file_directory is None:
          file_directory = ''
       if self.result['count'] is None:
          return None
       if plot_title is None:
          plot_title = self.result['circuit']
       plot_histogram(self.result['count'], title=plot_title).show()
       plt.savefig(os.path.join(file_directory,'histogram.png'))
    
