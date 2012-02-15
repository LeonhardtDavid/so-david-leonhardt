class Prog:
    def __init__(self, priority, name, code=[], vars=[]):
        self.name = name
        self.priority = priority
        self.code = code
        self.vars = vars
        self.maxBurst = self.calculateMaxBurst()
        self.lenght = self.calculateLenght()
    
    def calculateMaxBurst(self):
        maxBurst = 0
        for inst in self.code:
            if inst.cpuBurst() > maxBurst:
                maxBurst = inst.cpuBurst()
        return maxBurst
    
    def calculateLenght(self):
        lenght = 0
        for inst in self.code:
            lenght += inst.burst
        lenght += len(self.vars)
        return lenght
        
    def __repr__(self):
        return 'Prog "%s" %s' % (self.name, self.code)