import threading

from Signals import SignalCompact
from Signals import SignalLoad

class PLP:
    lock = threading.RLock()
    
    def __init__(self):
        self.new = []
    
    def add(self, kernel, pcb, prog, compact):#No necesita lock, el kernel usa este add desde un metodo sincronizado
        if kernel.canLoad(prog):
            kernel.interrupt(SignalLoad(pcb, prog))
            kernel.setQuantum(kernel.getCPUburstTime() * prog.maxBurst)
            kernel.scheduler.add(pcb.pid, kernel)
        elif compact:#???? No convence
            kernel.interrupt(SignalCompact())
            self.add(kernel, pcb, prog, False)
        else:
            self.new.append((pcb, prog))
    
    def reschedule(self, kernel):
        self.lock.acquire()
        try:
            for i in range(len(self.new)):
                next = self.new.pop(0)
                self.add(kernel, next[0], next[1], kernel.memCompact)
        finally:
            self.lock.release()
