import time

from Signals import SignalIO_REQ

class Instr:
#    
    def execute(self, resource):
        raise NotImplementedError("Deberias tener esto implementado")
    
    def getCodeBlock(self):
        codeBlock = []
        for i in range(self.burst):
            codeBlock.append(self)
        return codeBlock
#    
    def __repr__(self):
        raise NotImplementedError("Deberias tener esto implementado")

class InstrCPU(Instr):
    def __init__(self, burst=1):
        self.burst = burst
    
    def execute(self, resource):
        resource.pcb.setRunning()
        
        if not resource.kernel.kernelMode:
            print('[cpu] %s - %s' % (self, resource.pcb))
            time.sleep(resource.burstTime)
            resource.pcb.instNum = resource.pcb.instNum + 1
    
    def cpuBurst(self):
        return self.burst

    def __repr__(self):
        return 'CPU %d' % (self.burst)


class InstrCPUMov(InstrCPU):
    def __init__(self, var, val):
        self.burst = 1
        self.var = var
        self.val = val
    
    def execute(self, resource):
        resource.pcb.setRunning()
        
        if not resource.kernel.kernelMode:
            time.sleep(resource.burstTime * self.burst)
            print('[cpu] %s - %s' % (self, resource.pcb))
            instNum = resource.pcb.instNum
            resource.pcb.instNum = resource.get(self.var)
            resource.mmu.write(resource.pcb, self.val)
            resource.pcb.instNum = instNum
            resource.pcb.instNum = resource.pcb.instNum + 1
    
    def __repr__(self):
        return 'CPU-MOV %d' % (self.burst)


class InstrCPUSum(InstrCPU):
    def __init__(self, a, b):
        self.burst = 1
        self.a = a
        self.b = b
    
    def execute(self, resource):
        resource.pcb.setRunning()
        
        if not resource.kernel.kernelMode:
            time.sleep(resource.burstTime * self.burst)
            print('[cpu] %s - %s' % (self, resource.pcb))
            instNum = resource.pcb.instNum
            resource.pcb.instNum = resource.get(self.b)
            b = resource.mmu.read(resource.pcb) 
            resource.pcb.instNum = resource.get(self.a)
            a = resource.mmu.read(resource.pcb)
            a += b
            resource.mmu.write(resource.pcb, a)
            resource.pcb.instNum = instNum
            resource.pcb.instNum = resource.pcb.instNum + 1
    
    def __repr__(self):
        return 'CPU-SUMA %d' % (self.burst)

    
class InstrIO(Instr):
    def __init__(self, device, burst=1):
        self.device = device
        self.burst = burst
    
    def execute(self, resource):
        pcb = resource.pcb
        resource.pcb = None
        pcb.setWaiting()
        resource.kernel.interrupt(SignalIO_REQ(self, pcb.pid))
    
    def cpuBurst(self):
        return 0
    
    def send(self, pid):
        self.device.put((pid, self))

    def __repr__(self):
        return 'IO %d' % (self.burst)
