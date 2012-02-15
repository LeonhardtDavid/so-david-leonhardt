from States import New

class  PCB:
    
    def __init__(self, pid, priority, instNum, vars={}, state=New()):
        self.pid = pid
        self.priority = priority
        self.instNum = instNum
        self.base = None
        self.limit = None
        self.vars = vars
        self.pageList = []
        self.state = state
    
    def setReady(self):
        self.state.setReady(self)
    
    def setWaiting(self):
        self.state.setWaiting(self)
    
    def setNew(self):
        self.state.setNew(self)
    
    def setFinished(self):
        self.state.setFinished(self)
    
    def setRunning(self):
        self.state.setRunning(self)
    
    def __repr__(self):
        return '(%s, %s, %s)' % (self.pid, self.instNum, self.state)
