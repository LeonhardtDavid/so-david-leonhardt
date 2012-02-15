from Kernel import Kernel
from PCPs import PCProundRobin
from Resource import MMUbestAdj
from Resource import MMUPaging

class KernelFactory:
    def create(self):
        raise NotImplementedError("Deberias tener implementado esto")

class KernelRRbestAdjWcompactFact(KernelFactory):
    def __init__(self, memSize):
        self.memSize = memSize
    
    def create(self):
        return Kernel(PCProundRobin(), MMUbestAdj(self.memSize), True)

class KernelRRpagingFact(KernelFactory):
    def __init__(self, memSize, pageSize):
        self.memSize = memSize
        self.pageSize = pageSize
    
    def create(self):
        return Kernel(PCProundRobin(), MMUPaging(self.memSize, self.pageSize), False)