import threading

from Signals import SignalTimer

class TimerRR(threading.Thread):
    def __init__(self, kernel, quantum=1):
        threading.Thread.__init__(self)
        self.kernel = kernel
        self.quantum = quantum
        self.event = threading.Event()
    
    def run(self):
        self.event.wait(self.quantum)
        if not self.kernel.kernelMode and self.kernel.cpu.pcb is not None:
            self.kernel.interrupt(SignalTimer())
    
    def set(self):
        self.event.set()

class PCP:
    lock = threading.RLock()
    
    def __init__(self, quantum=None):
        self.ready = []
    
    def add(self, pid, kernel):
        self.lock.acquire()
        try:
            kernel.pcbt[pid].setReady()
            self.ready.append(pid)
        finally:
            self.lock.release()
    
    def popNextPid(self, kernel):
        self.lock.acquire()
        try:
            return self.ready.pop(0)
        finally:
            self.lock.release()
    
    def reschedule(self, kernel):
        self.lock.acquire()
        try:
            print('[kernel.sch] ready%s'%(self))
            print('[kernel.sch] %s'%(kernel.mmu))
            
            if kernel.cpu.pcb is not None: # save pcb if necesary
                kernel.pcbt[kernel.current_pid] = kernel.cpu.pcb
                self.add(kernel.current_pid, kernel)
                
            if len(self.ready) > 0:  # schedule next process
                if kernel.idle:
                    kernel.idle = False
                kernel.current_pid = self.popNextPid(kernel)
                kernel.cpu.pcb = kernel.pcbt[kernel.current_pid]
                print('[kernel.sch] scheduled pid %d'%(kernel.current_pid))
            else:
                kernel.set_idle()
        finally:
            self.lock.release()
    
    def setQuantum(self, quantum):
        pass
    
    def __repr__(self):
        return str(self.ready)


#class PCPfcfs(PCP):
#    def __init__(self, quantum=None):
#        self.ready = []


class PCPpriority(PCP):
#    def __init__(self, quantum=None):
#        self.ready = []
    
    def popNextPid(self, kernel):
        nextPid = self.ready[0]
        for i in self.ready:
            if kernel.pcbt[nextPid].priority > kernel.pcbt[i].priority:
                nextPid = i
        self.ready.remove(nextPid)
        return nextPid


class PCProundRobin(PCP):
    
    def __init__(self, quantum=1.0):
        self.ready = []
        self.quantum = quantum
        self.timer = TimerRR(self.quantum)
    
    def reschedule(self, kernel):
        self.timer.set()
        super(PCProundRobin, self).reschedule(kernel)
        if kernel.current_pid is not None:
            self.timer = TimerRR(kernel, self.quantum)
            self.timer.start()
    
    def setQuantum(self, quantum):
        if self.quantum < quantum:
            self.quantum = quantum


class PCProundRobinWithPriority(PCProundRobin):
    def popNextPid(self, kernel):
        nextPid = self.ready[0]
        for i in self.ready:
            if kernel.pcbt[nextPid].priority < kernel.pcbt[i].priority:
                nextPid = i
        self.ready.remove(nextPid)
        return nextPid
