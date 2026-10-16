from enum import IntEnum

class EstadoReclamoEnum(IntEnum):
    RECIBIDO = 1
    EN_EVALUACION = 2
    EN_INSPECCION = 3
    RESUELTO = 4
    NOTIFICADO = 5
 

class PrioridadReclamoEnum(IntEnum):
    NORMAL = 0
    URGENTE = 1

class RecurrenciaHechoEnum(IntEnum):
    PRIMERAVEZ = 1
    HECHOREITERADO = 2
    NOLOSE = 3