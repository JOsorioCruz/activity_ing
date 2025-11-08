"""
Excepciones personalizadas del sistema.
Facilita el manejo de errores específicos del dominio.
"""

from typing import Any, Optional


class NominaException(Exception):
    """Excepción base para el sistema de nómina."""

    def __init__(
            self,
            message: str,
            code: str = "NOMINA_ERROR",
            details: Optional[dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class EmpleadoNoEncontradoException(NominaException):
    """Empleado no encontrado en la base de datos."""

    def __init__(self, empleado_id: int):
        super().__init__(
            message=f"Empleado con ID {empleado_id} no encontrado",
            code="EMPLEADO_NOT_FOUND",
            details={"empleado_id": empleado_id}
        )


class PeriodoNoEncontradoException(NominaException):
    """Período de nómina no encontrado."""

    def __init__(self, periodo_id: int):
        super().__init__(
            message=f"Período con ID {periodo_id} no encontrado",
            code="PERIODO_NOT_FOUND",
            details={"periodo_id": periodo_id}
        )


class SalarioNegativoException(NominaException):
    """Salario neto resulta negativo."""

    def __init__(self, salario_neto: float, empleado_id: int):
        super().__init__(
            message=f"El salario neto no puede ser negativo: {salario_neto}",
            code="SALARIO_NEGATIVO",
            details={
                "salario_neto": salario_neto,
                "empleado_id": empleado_id
            }
        )


class ValidacionNominaException(NominaException):
    """Error en validación de datos de nómina."""

    def __init__(self, campo: str, mensaje: str):
        super().__init__(
            message=f"Error de validación en {campo}: {mensaje}",
            code="VALIDACION_ERROR",
            details={"campo": campo}
        )


class PeriodoCerradoException(NominaException):
    """Intento de modificar período cerrado."""

    def __init__(self, periodo_id: int):
        super().__init__(
            message=f"El período {periodo_id} está cerrado y no puede modificarse",
            code="PERIODO_CERRADO",
            details={"periodo_id": periodo_id}
        )