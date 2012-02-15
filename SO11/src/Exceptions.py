class StateException(Exception):
    def __str__(self):
        return "Cambio de estado invalido"


class MemoryOverLoad(Exception):
    def __str__(self):
        return "Memoria insuficiente"