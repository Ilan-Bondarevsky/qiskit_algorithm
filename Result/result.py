
class ResultData:
    def __init__(self, job) -> None:
        self.job = job
        self.result = job.result()
        
    def get_result(self):
        return self.result
    
    def get_counts(self, experiment = None):
        return self.result.get_counts(experiment)
    
    def get_memory(self, experiment = None):
        return self.result.get_memory(experiment)
    
    def get_statevector(self, experiment = None, decimals = None):
        return self.result.get_statevector(experiment, decimals)
    
    def get_unitary(self, experiment = None, decimals=None):
        return self.result.get_unitary(experiment, decimals)
    
    def to_dict(self):
        return self.result.to_dict()
    
    def get_data(self, experiment=None):
        return self.result.data(experiment)
    
    def get_job_id(self):
        return self.job.job_id()
    
    def get_job_backend(self):
        return self.job.backend()
    
    def check_job_done(self):
        return self.job.done()
        
    def check_job_running(self):
        return self.job.running()
    
    def job_status(self):
        return self.job.status()
    
    def job_cancelled(self):
        return self.job.cancelled()
    
    def check_job_final_state(self):
        return self.job.in_final_state()
    