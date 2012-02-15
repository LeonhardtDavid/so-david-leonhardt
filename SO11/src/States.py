from Exceptions import StateException

class State:
    def setReady(self, pcb):
        raise StateException()
    
    def setWaiting(self, pcb):
        raise StateException()
    
    def setNew(self, pcb):
        raise StateException()
    
    def setFinished(self, pcb):
        raise StateException()
    
    def setRunning(self, pcb):
        raise StateException()
    
    def __repr__(self, pcb):
        raise NotImplementedError("Deberias tener implementado esto")

class Ready(State):
    def setReady(self, pcb):
        pcb.state = Ready()
    
    def setWaiting(self, pcb):
        pcb.state = Waiting()
    
    def setFinished(self, pcb):
        pcb.state = Finished()
    
    def setRunning(self, pcb):
        pcb.state = Running()
    
    def __repr__(self):
        return "Ready"

class Waiting(State):
    def setReady(self, pcb):
        pcb.state = Ready()
    
    def setWaiting(self, pcb):
        pcb.state = Waiting()
    
    def __repr__(self):
        return "Waiting"

class New(State):
    def setReady(self, pcb):
        pcb.state = Ready()
    
    def setNew(self, pcb):
        pcb.state = New()
    
    def __repr__(self):
        return "New"

class Finished(State):
    ####################################################################################
    def setReady(self, pcb):############ESTO NO TIENE QUE IR, VER PORQUE SE GENERA LA EXCEPCION
        pcb.state = Ready()
        ####################################################################################
    
    def setFinished(self, pcb):
        pcb.state = Finished()
    
    def __repr__(self):
        return "Finished"

class Running(State):
    def setReady(self, pcb):
        pcb.state = Ready()
    
    def setWaiting(self, pcb):
        pcb.state = Waiting()
    
    def setFinished(self, pcb):
        pcb.state = Finished()
    
    def setRunning(self, pcb):
        pcb.state = Running()
    
    def __repr__(self):
        return "Running"
