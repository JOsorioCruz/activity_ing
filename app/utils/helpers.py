"""
Funciones auxiliares y utilidades comunes.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from dateutil.relativedelta import relativedelta


def calcular_anios_antiguedad(fecha_ingreso: date, fecha_referencia: Optional[date] = None) -> int:
    """
    Calcula los años de antigüedad de un empleado.

    Args:
        fecha_ingreso: Fecha de ingreso del empleado
        fecha_referencia: Fecha de referencia (por defecto hoy)

    Returns:
        int: Años completos de antigüedad
    """
    if fecha_referencia is None:
        fecha_referencia = date.today()

    diferencia = relativedelta(fecha_referencia, fecha_ingreso)
    return diferencia.years


def redondear_decimal(valor: float, decimales: int = 2) -> Decimal:
    """
    Redondea un valor a un número específico de decimales.

    Args:
        valor: Valor a redondear
        decimales: Número de decimales

    Returns:
        Decimal: Valor redondeado
    """
    return Decimal(str(round(valor, decimales)))


def calcular_porcentaje(valor: float, porcentaje: float) -> Decimal:
    """
    Calcula el porcentaje de un valor.

    Args:
        valor: Valor base
        porcentaje: Porcentaje a aplicar

    Returns:
        Decimal: Resultado del cálculo
    """
    resultado = (valor * porcentaje) / 100
    return redondear_decimal(resultado)


def validar_horas(horas: float) -> bool:
    """
    Valida que las horas sean un valor válido.

    Args:
        horas: Número de horas

    Returns:
        bool: True si es válido
    """
    return horas >= 0


def validar_ventas(ventas: float) -> bool:
    """
    Valida que las ventas sean un valor válido.

    Args:
        ventas: Monto de ventas

    Returns:
        bool: True si es válido
    """
    return ventas >= 0


def calcular_anio_antiguedad(fecha_ingreso: date, fecha_referencia: Optional[date] = None) -> int:
    """Compatibilidad: wrapper que devuelve los años completos de antigüedad.

    Esta función mantiene la API usada en otros módulos del proyecto.
    """
    return calcular_anios_antiguedad(fecha_ingreso, fecha_referencia)
