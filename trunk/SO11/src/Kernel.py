import threading
import sys

from Signals import SignalNew
from Resource import CPU
from Resource import IO
from Process import PCB
from PLP import PLP


class Kernel:
    lock = threading.RLock()
    
    def __init__(self, schedulerType, mmuType, memCompact):
        self.running = False
        self.kernelMode = False
        self.mmu = mmuType
        self.pcbt = {}
        self.cpu = None
        self.io = None
        self.pid_counter = 0
        self.current_pid = None
        self.idle = True
        self.scheduler = schedulerType
        self.longScheduler = PLP()
        self.memCompact = memCompact
    
    def  start(self):
        print('[kernel] starting...')
        
        if not self.running:
            self.running = 1
            self.cpu = CPU(self, self.mmu)
            self.cpu.start()
            self.io = IO(self)
            self.io.start()
            print('[kernel] started.')
        
    def stop(self):
        self.running = False
        sys.exit(0)
    
    def interrupt(self, signal):
        self.lock.acquire()
        
        self.kernelMode = True
        
        try: 
            signal.execute(self)
        finally:
            self.kernelMode = False
            self.lock.release()
    
    def run(self, prog): 
        self.lock.acquire()
        
        try:
            pid = self.pid_counter
            self.pid_counter = self.pid_counter + 1
            self.pcbt[pid] = PCB(pid, prog.priority, 0)
            self.longScheduler.add(self, self.pcbt[pid], prog, self.memCompact)
        finally:
            self.lock.release()
        
        print('[kernel.run] pid %d: %s'%(pid, prog))
        
        self.interrupt(SignalNew())
    
    def setQuantum(self, quantum):
        self.scheduler.setQuantum(quantum)
    
    def getCPUburstTime(self):
        return self.cpu.burstTime
    
    def canLoad(self, prog):
        return self.mmu.canLoad(prog)
    
    def load(self, pcb, prog):
        self.mmu.load(pcb, prog)
    
    def longReschedule(self):
        self.longScheduler.reschedule(self)
    
    def reschedule(self):
        self.scheduler.reschedule(self)
    
    def compact(self):
        self.mmu.compact(self.pcbt)
        
    def exit(self):
        self.cpu.pcb = None
        self.mmu.unload(self.pcbt[self.current_pid])
        del self.pcbt[self.current_pid]
        self.current_pid = None
    
    def set_idle(self):
        self.idle = True
