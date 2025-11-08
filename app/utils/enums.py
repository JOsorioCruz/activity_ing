"""
Enumeraciones del sistema.
Centraliza valores constantes y estados.
"""

from enum import Enum


class TipoEmpleadoEnum(str, Enum):
    """Tipos de empleado según reglas de negocio."""
    ASALARIADO = "ASALARIADO"
    POR_HORAS = "POR_HORAS"
    POR_COMISION = "POR_COMISION"
    TEMPORAL = "TEMPORAL"


class EstadoEmpleadoEnum(str, Enum):
    """Estados posibles de un empleado."""
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    SUSPENDIDO = "SUSPENDIDO"


class EstadoPeriodoEnum(str, Enum):
    """Estados del período de nómina."""
    ABIERTO = "ABIERTO"
    EN_PROCESO = "EN_PROCESO"
    CERRADO = "CERRADO"
    PAGADO = "PAGADO"


class TipoBonoEnum(str, Enum):
    """Tipos de bonos según reglas de negocio."""
    BONO_ANTIGUEDAD = "BONO_ANTIGUEDAD"
    BONO_VENTAS = "BONO_VENTAS"


class TipoBeneficioEnum(str, Enum):
    """Tipos de beneficios."""
    BONO_ALIMENTACION = "BONO_ALIMENTACION"
    FONDO_AHORRO = "FONDO_AHORRO"


class TipoDeduccionEnum(str, Enum):
    """Tipos de deducciones."""
    SEGURIDAD_SOCIAL_PENSION = "SEGURIDAD_SOCIAL_PENSION"
    ARL = "ARL"
    FONDO_AHORRO_EMPLEADO = "FONDO_AHORRO_EMPLEADO"