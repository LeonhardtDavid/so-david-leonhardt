class Signal:
    def execute(self, kernel):
        raise NotImplementedError("Deberias tener esto implementado")

class SignalExit(Signal):
    def execute(self, kernel):
        print('[signal] exit pid %s'%(kernel.current_pid))
        kernel.exit()
        kernel.longReschedule()
        kernel.reschedule()

class SignalTimer(Signal):
    def execute(self, kernel):
        print('[signal] timer')
        kernel.reschedule()

class SignalIO_REQ(Signal):
    def __init__(self, inst, pid):
        self.inst = inst
        self.pid = pid
    
    def execute(self, kernel):
        print('[signal] io_req')
        self.inst.send(self.pid)
#        kernel.ioExec(self.pcb)
        kernel.reschedule()

class SignalIO_END(Signal):
    def execute(self, kernel):
        print('[signal] io_end')
        if kernel.idle:
            kernel.reschedule()

class SignalKill(Signal):
    def execute(self, kernel):
        print('[signal] kill')
        kernel.interrupt(SignalExit())

class SignalNew(Signal):
    def execute(self, kernel):
        print('[signal] new')
        if kernel.idle:
            kernel.reschedule()

class SignalCompact(Signal):
    def execute(self, kernel):
        print('[signal] memory_compact')
        kernel.compact()

class SignalLoad(Signal):
    def __init__(self, pcb, prog):
        self.pcb = pcb
        self.prog = prog
    
    def execute(self, kernel):
        print('[signal] load_program')
        kernel.load(self.pcb, self.prog)
