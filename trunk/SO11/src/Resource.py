import threading
import time
from queue import Queue

from Signals import SignalExit
from Signals import SignalIO_END
from Exceptions import MemoryOverLoad


class Memory:
    def __init__(self, lenght):
        self.memory = {}
        self.lenght = lenght
    
    def write(self, address, val):
        if address >= 0 and address < self.lenght:
            self.memory[address] = val
        else:
            raise MemoryOverLoad()
    
    def read(self, address):
        return self.memory[address]
    
    def __repr__(self):
        return '%s' %(self.memory)


class MMUbase:
    def canLoad(self, prog):
        raise NotImplementedError("Deberias tener implementado esto")
    
    def getCode(self, prog):
        code = []
        for inst in prog.code:
            code = code + inst.getCodeBlock()
        return code
    
    def load(self, pcb, prog):
        raise NotImplementedError("Deberias tener implementado esto")
    
    def unload(self, pcb):
        raise NotImplementedError("Deberias tener implementado esto")
    
    def read(self, pcb):
        raise NotImplementedError("Deberias tener implementado esto")
    
    def write(self, pcb):
        raise NotImplementedError("Deberias tener implementado esto")
    
    def __repr__(self):
        raise NotImplementedError("Deberias tener implementado esto")


class MMUContAssoc(MMUbase):
    def __init__(self, memSize):
        self.memory = Memory(memSize)
        self.freeSpace = [(0, memSize-1)] #(principio, fin)
    
    def canLoad(self, prog):
        i = 0
        can = False
        while i < len(self.freeSpace) and not can:
            if self.freeSpace[i][1] - self.freeSpace[i][0] >= prog.lenght - 1:
                can = True
            i += 1
        return can
    
    def getFreeBlock(self, space):
        raise NotImplementedError("Deberias tener implementado esto")
    
    def assignVars(self, pcb, prog, position):
        for var in prog.vars:
            pcb.vars[var] = position
            position += 1
    
    def assignBaseAndLimit(self, freeBlock, pcb, prog):
        pcb.base = freeBlock[0]
        if freeBlock[1] - freeBlock[0] > prog.lenght - 1:
            freeBlock = freeBlock[0] + prog.lenght, freeBlock[1]
            self.freeSpace.append(freeBlock)
        pcb.limit = prog.lenght - 1
    
    def load(self, pcb, prog):
        #Debe utilizarse el metodo canLoad para asegurar el correcto funcionamiento de este metodo.
        freeBlock = self.getFreeBlock(prog.lenght)
        code = self.getCode(prog)
        for i in range(len(code)):
            self.memory.write(freeBlock[0] + i, code[i])
        self.assignVars(pcb, prog, len(code))
        self.assignBaseAndLimit(freeBlock, pcb, prog)
    
    def sortFreeBlocks(self):
        i = 0
        while i < len(self.freeSpace)-1:
            if self.freeSpace[i][0] > self.freeSpace[i+1][0]:
                x = self.freeSpace[i]
                self.freeSpace[i] = self.freeSpace[i+1]
                self.freeSpace[i+1] = x
            i += 1
    
    def compactFreeBlocks(self):
        self.sortFreeBlocks()
        i = 0
        while i < len(self.freeSpace)-1:
            if self.freeSpace[i][1] + 1 == self.freeSpace[i+1][0]:
                self.freeSpace[i] = self.freeSpace[i][0], self.freeSpace[i+1][1]
                del self.freeSpace[i+1]
            else:
                i += 1
    
    def unload(self, pcb):
        self.freeSpace.append((pcb.base, pcb.base + pcb.limit))
        self.compactFreeBlocks()

    def read(self, pcb):
        if pcb.instNum > pcb.limit:
            return None
        else:   
            return self.memory.read(pcb.base + pcb.instNum)
    
    def write(self, pcb, val):
        if pcb.instNum <= pcb.limit:
            self.memory.write(pcb.base + pcb.instNum, val)
    
    def compact(self, pcbt, blockNum = 0):
        if len(self.freeSpace) - blockNum > 1:
            for key in pcbt:
                pcb = pcbt[key]
                if self.freeSpace[blockNum][1] + 1 == pcb.base:
                    base = pcb.base
                    limit = pcb.limit
                    pcb.base = self.freeSpace[blockNum][0]
                    self.freeSpace[blockNum] = base, base + limit
                    self.compactFreeBlocks()
            self.compact(pcbt, blockNum + 1)
    
    def __repr__(self):
        return 'memory%s\n\tfree space%s'%(self.memory, self.freeSpace)


class MMUfirstAdj(MMUContAssoc):
    def getFreeBlock(self, space):
        i = 0
        freeBlock = None
        while freeBlock is None and i < len(self.freeSpace):
            if self.freeSpace[i][1] - self.freeSpace[i][0] + 1 >= space:
                freeBlock = self.freeSpace.pop(i)
            i += 1
        return freeBlock


class MMUbestAdj(MMUContAssoc):
    def getFreeBlock(self, space):
        freeBlockNum = 0
        freeBlock = None
        
        for i in range(len(self.freeSpace)):
            freeSpaceLong = self.freeSpace[i][1] - self.freeSpace[i][0] + 1
            if freeSpaceLong >= space and freeSpaceLong < self.freeSpace[freeBlockNum][1] - self.freeSpace[freeBlockNum][0]:
                freeBlockNum = i
        
        if len(self.freeSpace) > 0 and self.freeSpace[freeBlockNum][1] - self.freeSpace[freeBlockNum][0] + 1 >= space:
            freeBlock = self.freeSpace.pop(freeBlockNum)
        
        return freeBlock


class MMUworstAdj(MMUContAssoc):
    def getFreeBlock(self, space):
        freeBlockNum = 0
        freeBlock = None
        
        for i in range(len(self.freeSpace)):
            freeSpaceLong = self.freeSpace[i][1] - self.freeSpace[i][0] + 1
            if freeSpaceLong >= space and freeSpaceLong > self.freeSpace[freeBlockNum][1] - self.freeSpace[freeBlockNum][0]:
                freeBlockNum = i
        
        if len(self.freeSpace) > 0 and self.freeSpace[freeBlockNum][1] - self.freeSpace[freeBlockNum][0] + 1 >= space:
            freeBlock = self.freeSpace.pop(freeBlockNum)
        
        return freeBlock


class MMUPaging(MMUbase):
    def __init__(self, memSize, pageSize):
        self.memory = Memory(memSize)
        self.pageSize = pageSize
        self.pageList = self.createPageList(memSize)
        self.freePages = self.createfreePages(memSize)
    
    def createPageList(self, memSize):
        pages = {}
        pageQuant = memSize // self.pageSize
        pages[0] = 0
        for i in range(1, pageQuant):
            pages[i] = i * self.pageSize
        return pages
    
    def createfreePages(self, memSize):
        freePages = []
        pageQuant = memSize // self.pageSize
        for i in range(pageQuant):
            freePages.append(i)
        return freePages
    
    def canLoad(self, prog):
        quant = prog.lenght // self.pageSize
        if prog.lenght % self.pageSize > 0:
            quant += 1
        return quant <= len(self.freePages) 
    
    def assignVars(self, pcb, prog, page, position):
        for var in prog.vars:
            if position % self.pageSize == 0:
                page = self.freePages.pop(0)
                pcb.pageList.append(page)
            pcb.vars[var] = position
            position += 1
    
    def load(self, pcb, prog):
        #Debe utilizarse el metodo canLoad para asegurar el correcto funcionamiento de este metodo.
        code = self.getCode(prog)
        displacement = 0
        for i in range(len(code)):
            if i % self.pageSize == 0:
                page = self.freePages.pop(0)
                pcb.pageList.append(page)
                displacement = 0
            self.memory.write(self.pageList[page] + displacement, code[i])
            displacement += 1
        self.assignVars(pcb, prog, page, len(code))
        pcb.limit = len(code) + len(prog.vars) - 1
    
    def unload(self, pcb):
        self.freePages = self.freePages + pcb.pageList
    
    def read(self, pcb):
        if pcb.instNum > pcb.limit:
            return None
        else:
            return self.memory.read(self.pageList[pcb.pageList[pcb.instNum//self.pageSize]] + pcb.instNum % self.pageSize)
    
    def write(self, pcb, val):
        if pcb.instNum <= pcb.limit:
            self.memory.write(self.pageList[pcb.pageList[pcb.instNum//self.pageSize]] + pcb.instNum % self.pageSize, val)
    
    def __repr__(self):
        return 'memory%s\n\tpage list%s\n\tfree pages%s'%(self.memory, self.pageList, self.freePages)


class CPU(threading.Thread):
    
    def __init__(self, kernel, mmu):
        threading.Thread.__init__(self)
        self.pcb = None
        self.mmu = mmu
        self.kernel = kernel
        self.burstTime = 0.5
        
    def run(self):
        while self.kernel.running: # CPU run while system is running
            if self.pcb is not None:
                if self.pcb.instNum > self.pcb.limit - len(self.pcb.vars):
                    instr = None
                else:
                    instr = self.mmu.read(self.pcb)
                
                if instr is None:
                    self.pcb.setFinished()
                    self.kernel.interrupt(SignalExit())
                else:
                    instr.execute(self)
                    
            else:
                time.sleep(0.1) # idle
    
    def get(self, var):
        return self.pcb.vars[var]


class IO(threading.Thread):
    
    def __init__(self, kernel):
        threading.Thread.__init__(self)
        self.queue = Queue()
        self.kernel = kernel
    
    def run(self):
        while self.kernel.running:
            if self.queue.qsize() > 0:
                pid, instr = self.queue.get()
                pcb = self.kernel.pcbt[pid]
                print('[io] %s - %s' % (instr, pcb))
                time.sleep(1.0)
                pcb.instNum = pcb.instNum + 1
                self.kernel.scheduler.add(pid, self.kernel)
                self.kernel.interrupt(SignalIO_END())
    
    def put(self, pid_IO):
        self.queue.put(pid_IO)
