import hashlib
import cloudpickle
import pandas as pd
import sys

class SpartaqubePlotSession:

    def __init__(self):
        self.trunc = 512
        self.all_hash_server = []
        self.all_hash_notebook = []
        
    # def get_hash(self, var, trunc=None):
    #     '''
        
    #     '''
    #     if trunc is None:
    #         trunc = self.trunc
    #     serialized = cloudpickle.dumps(var).decode('latin1')
    #     full_hash = hashlib.sha256(serialized).hexdigest()
    #     partial_hash = full_hash[:trunc]
    #     if partial_hash in list(self.plot_variables_session.keys()):
    #         return self.get_hash(var, trunc+1)

    #     return partial_hash

    def get_all_hash_server(self) -> list:
        return self.all_hash_server
    
    def get_all_hash_notebook_list(self) -> list:
        return self.all_hash_notebook
    
    def set_hash_server_list(self, all_hash_server) -> list:
        self.all_hash_server = all_hash_server

    def has_hash(self, var) -> bool:
        '''
        Test if variable has hash
        '''
        return self.is_hash_in_session(self.get_hash(var))
    
    def is_hash_in_session(self, hash) -> bool:
        '''
        
        '''
        return hash in self.all_hash_server
    
    def get_hash(self, var) -> str:
        '''
        
        '''
        serialized = cloudpickle.dumps(var) #.decode('latin1')
        full_hash = hashlib.sha256(serialized).hexdigest()
        partial_hash = full_hash[:self.trunc]
        return partial_hash

    def add_hash(self, hash):
        '''
        
        '''
        if hash not in list(self.all_hash_server):
            self.all_hash_server.append(hash)

    def add_to_all_hash_notebook(self, hash):
        '''
        
        '''
        if hash not in list(self.all_hash_notebook):
            self.all_hash_notebook.append(hash)

    def clear_cache(self):
        self.all_hash_server = []
        self.all_hash_notebook = []