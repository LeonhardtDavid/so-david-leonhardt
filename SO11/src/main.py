from Factory import KernelRRbestAdjWcompactFact
from Factory import KernelRRpagingFact
from Program import Prog
from Instructions import InstrCPU
from Instructions import InstrIO
from Instructions import InstrCPUMov
from Instructions import InstrCPUSum


def main():
    memSize = 64
    pageSize = 4
    
#    fact = KernelRRbestAdjWcompactFact(memSize)
    fact = KernelRRpagingFact(memSize, pageSize)
    
    kernel = fact.create()
    kernel.start()
    
    prog = Prog(0, 'test.c', [InstrCPU(), InstrCPU(2), InstrIO(kernel.io, 5), InstrCPU(4)])#, ['a', 'b'])
    prog1 = Prog(1, 'test1.c', [InstrIO(kernel.io, 5), InstrCPU(2), InstrIO(kernel.io, 2), InstrCPU(4)])
    prog2 = Prog(0, 'test2.c', [InstrCPUMov('a', 1), InstrCPUMov('b', 5), InstrCPUSum('a', 'b'), InstrIO(kernel.io, 2)], ['a', 'b'])
    
    kernel.run(prog)
    kernel.run(prog1)
    
    # time.sleep(5)
    
    kernel.run(prog)
    kernel.run(prog)
    
    kernel.run(prog2)
    
    
main()
