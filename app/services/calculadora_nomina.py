"""
Servicio de Calculadora de Nómina.
Contiene la lógica de negocio para calcular salarios según tipo de empleado.

Principios SOLID aplicados:
- Single Responsibility: Solo calcula nóminas
- Open/Closed: Extensible para nuevos tipos de empleado
"""

from decimal import Decimal
from datetime import date
from typing import Dict, Tuple

from app.models.empleado import Empleado
from app.models.tipo_empleado import TipoEmpleado
from app.utils.enums import TipoEmpleadoEnum
from app.utils.helpers import (
    calcular_anio_antiguedad,
    calcular_porcentaje,
    redondear_decimal
)
from app.utils.exceptions import ValidacionNominaException

# Constantes del negocio
BONO_ANTIGUEDAD_PORCENTAJE = Decimal("10.00")  # 10%
anio_PARA_BONO_ANTIGUEDAD = 5

BONO_ALIMENTACION = Decimal("1000000.00")  # $1.000.000

COMISION_VENTAS_LIMITE = Decimal("20000000.00")  # $20.000.000
BONO_VENTAS_PORCENTAJE = Decimal("3.00")  # 3%

HORAS_NORMALES_MAXIMAS = Decimal("40.00")  # 40 horas
MULTIPLICADOR_HORA_EXTRA = Decimal("1.5")  # 1.5x

DEDUCCION_SEGURIDAD_SOCIAL_PENSION = Decimal("4.00")  # 4%
DEDUCCION_ARL = Decimal("0.522")  # 0.522%

FONDO_AHORRO_PORCENTAJE = Decimal("2.00")  # 2%
anio_PARA_FONDO_AHORRO = 1


class CalculadoraNomina:
    """
    Calculadora de nómina con todas las reglas de negocio.

    Esta clase aplica el patrón Strategy implícitamente,
    ya que calcula según el tipo de empleado.
    """

    @staticmethod
    def calcular_salario_bruto(
            empleado: Empleado,
            horas_trabajadas: Decimal = Decimal("0"),
            horas_extras: Decimal = Decimal("0"),
            ventas_realizadas: Decimal = Decimal("0")
    ) -> Decimal:
        """
        Calcula el salario bruto según el tipo de empleado.

        Args:
            empleado: Objeto empleado
            horas_trabajadas: Horas trabajadas (para POR_HORAS)
            horas_extras: Horas extras (para POR_HORAS)
            ventas_realizadas: Ventas (para POR_COMISION)

        Returns:
            Salario bruto calculado

        Raises:
            ValidacionNominaException: Si hay error en validación
        """
        tipo_nombre = empleado.tipo_empleado.nombre_tipo

        if tipo_nombre == TipoEmpleadoEnum.ASALARIADO.value:
            return CalculadoraNomina._calcular_asalariado(empleado)

        elif tipo_nombre == TipoEmpleadoEnum.POR_HORAS.value:
            return CalculadoraNomina._calcular_por_horas(
                empleado, horas_trabajadas, horas_extras
            )

        elif tipo_nombre == TipoEmpleadoEnum.POR_COMISION.value:
            return CalculadoraNomina._calcular_por_comision(
                empleado, ventas_realizadas
            )

        elif tipo_nombre == TipoEmpleadoEnum.TEMPORAL.value:
            return CalculadoraNomina._calcular_temporal(empleado)

        else:
            raise ValidacionNominaException(
                "tipo_empleado",
                f"Tipo de empleado no soportado: {tipo_nombre}"
            )

    @staticmethod
    def _calcular_asalariado(empleado: Empleado) -> Decimal:
        """Calcula salario bruto para empleado asalariado."""
        return Decimal(str(empleado.salario_base or 0))

    @staticmethod
    def _calcular_por_horas(
            empleado: Empleado,
            horas_trabajadas: Decimal,
            horas_extras: Decimal
    ) -> Decimal:
        """
        Calcula salario bruto para empleado por horas.

        Regla: Horas normales + (Horas extras * 1.5)
        """
        if horas_trabajadas < 0:
            raise ValidacionNominaException(
                "horas_trabajadas",
                "Las horas trabajadas no pueden ser negativas"
            )

        if horas_extras < 0:
            raise ValidacionNominaException(
                "horas_extras",
                "Las horas extras no pueden ser negativas"
            )

        tarifa = Decimal(str(empleado.tarifa_hora or 0))

        # Salario por horas normales
        pago_normal = horas_trabajadas * tarifa

        # Pago por horas extras (1.5x)
        pago_extras = horas_extras * tarifa * MULTIPLICADOR_HORA_EXTRA

        return redondear_decimal(float(pago_normal + pago_extras))

    @staticmethod
    def _calcular_por_comision(
            empleado: Empleado,
            ventas_realizadas: Decimal
    ) -> Decimal:
        """
        Calcula salario bruto para empleado por comisión.

        Regla: Salario base + (Ventas * Porcentaje comisión)
        """
        if ventas_realizadas < 0:
            raise ValidacionNominaException(
                "ventas_realizadas",
                "Las ventas no pueden ser negativas"
            )

        salario_base = Decimal(str(empleado.salario_base or 0))
        porcentaje_comision = Decimal(str(empleado.porcentaje_comision or 0))

        # Calcular comisión
        comision = calcular_porcentaje(
            float(ventas_realizadas),
            float(porcentaje_comision)
        )

        return salario_base + comision

    @staticmethod
    def _calcular_temporal(empleado: Empleado) -> Decimal:
        """Calcula salario bruto para empleado temporal."""
        return Decimal(str(empleado.salario_base or 0))

    @staticmethod
    def calcular_bonos(
            empleado: Empleado,
            ventas_realizadas: Decimal = Decimal("0")
    ) -> Tuple[Decimal, Dict[str, Dict]]:
        """
        Calcula todos los bonos aplicables al empleado.

        Returns:
            Tupla con (total_bonos, detalles_bonos)
        """
        bonos = {}
        total = Decimal("0")

        tipo_nombre = empleado.tipo_empleado.nombre_tipo

        # Bono de antigüedad (solo para ASALARIADO)
        if tipo_nombre == TipoEmpleadoEnum.ASALARIADO.value:
            anio_antiguedad = calcular_anio_antiguedad(empleado.fecha_ingreso)

            if anio_antiguedad >= anio_PARA_BONO_ANTIGUEDAD:
                monto_bono = calcular_porcentaje(
                    float(empleado.salario_base),
                    float(BONO_ANTIGUEDAD_PORCENTAJE)
                )

                bonos["BONO_ANTIGUEDAD"] = {
                    "tipo_bono": "BONO_ANTIGUEDAD",
                    "descripcion": f"Bono por {anio_antiguedad} anio de antigüedad",
                    "monto": monto_bono,
                    "porcentaje_aplicado": BONO_ANTIGUEDAD_PORCENTAJE
                }

                total += monto_bono

        # Bono por ventas (solo para POR_COMISION)
        if tipo_nombre == TipoEmpleadoEnum.POR_COMISION.value:
            if ventas_realizadas > COMISION_VENTAS_LIMITE:
                monto_bono = calcular_porcentaje(
                    float(ventas_realizadas),
                    float(BONO_VENTAS_PORCENTAJE)
                )

                bonos["BONO_VENTAS"] = {
                    "tipo_bono": "BONO_VENTAS",
                    "descripcion": f"Bono por ventas superiores a ${COMISION_VENTAS_LIMITE:,.0f}",
                    "monto": monto_bono,
                    "porcentaje_aplicado": BONO_VENTAS_PORCENTAJE
                }

                total += monto_bono

        return total, bonos

    @staticmethod
    def calcular_beneficios(empleado: Empleado) -> Tuple[Decimal, Dict[str, Dict]]:
        """
        Calcula todos los beneficios aplicables al empleado.

        Returns:
            Tupla con (total_beneficios, detalles_beneficios)
        """
        beneficios = {}
        total = Decimal("0")

        tipo_nombre = empleado.tipo_empleado.nombre_tipo

        # Bono de alimentación (ASALARIADO y POR_COMISION)
        if tipo_nombre in [TipoEmpleadoEnum.ASALARIADO.value, TipoEmpleadoEnum.POR_COMISION.value]:
            beneficios["BONO_ALIMENTACION"] = {
                "tipo_beneficio": "BONO_ALIMENTACION",
                "descripcion": "Subsidio de alimentación mensual",
                "monto": BONO_ALIMENTACION
            }
            total += BONO_ALIMENTACION

        # Fondo de ahorro (POR_HORAS con más de 1 año)
        if tipo_nombre == TipoEmpleadoEnum.POR_HORAS.value:
            anio_antiguedad = calcular_anio_antiguedad(empleado.fecha_ingreso)

            if anio_antiguedad >= anio_PARA_FONDO_AHORRO and empleado.acepta_fondo_ahorro:
                # El fondo de ahorro es un beneficio empresarial (no se descuenta)
                # Nota: También habrá una deducción del empleado
                beneficio_fondo = Decimal("0")  # Puede configurarse si la empresa aporta

                if beneficio_fondo > 0:
                    beneficios["FONDO_AHORRO"] = {
                        "tipo_beneficio": "FONDO_AHORRO",
                        "descripcion": "Aporte empresarial a fondo de ahorro",
                        "monto": beneficio_fondo
                    }
                    total += beneficio_fondo

        return total, beneficios

    @staticmethod
    def calcular_deducciones(
            empleado: Empleado,
            salario_bruto: Decimal
    ) -> Tuple[Decimal, Dict[str, Dict]]:
        """
        Calcula todas las deducciones obligatorias.

        Returns:
            Tupla con (total_deducciones, detalles_deducciones)
        """
        deducciones = {}
        total = Decimal("0")

        # Seguridad Social y Pensión (4%)
        deduccion_ss = calcular_porcentaje(
            float(salario_bruto),
            float(DEDUCCION_SEGURIDAD_SOCIAL_PENSION)
        )

        deducciones["SEGURIDAD_SOCIAL_PENSION"] = {
            "tipo_deduccion": "SEGURIDAD_SOCIAL_PENSION",
            "descripcion": "Aporte a Seguridad Social y Pensión",
            "monto": deduccion_ss,
            "porcentaje_aplicado": DEDUCCION_SEGURIDAD_SOCIAL_PENSION,
            "base_calculo": salario_bruto
        }
        total += deduccion_ss

        # ARL (0.522%)
        deduccion_arl = calcular_porcentaje(
            float(salario_bruto),
            float(DEDUCCION_ARL)
        )

        deducciones["ARL"] = {
            "tipo_deduccion": "ARL",
            "descripcion": "Aporte a Riesgos Laborales",
            "monto": deduccion_arl,
            "porcentaje_aplicado": DEDUCCION_ARL,
            "base_calculo": salario_bruto
        }
        total += deduccion_arl

        # Fondo de ahorro del empleado (solo POR_HORAS con más de 1 año)
        tipo_nombre = empleado.tipo_empleado.nombre_tipo
        if tipo_nombre == TipoEmpleadoEnum.POR_HORAS.value:
            anio_antiguedad = calcular_anio_antiguedad(empleado.fecha_ingreso)

            if anio_antiguedad >= anio_PARA_FONDO_AHORRO and empleado.acepta_fondo_ahorro:
                deduccion_fondo = calcular_porcentaje(
                    float(salario_bruto),
                    float(FONDO_AHORRO_PORCENTAJE)
                )

                deducciones["FONDO_AHORRO_EMPLEADO"] = {
                    "tipo_deduccion": "FONDO_AHORRO_EMPLEADO",
                    "descripcion": "Aporte del empleado a fondo de ahorro",
                    "monto": deduccion_fondo,
                    "porcentaje_aplicado": FONDO_AHORRO_PORCENTAJE,
                    "base_calculo": salario_bruto
                }
                total += deduccion_fondo

        return total, deducciones

    @staticmethod
    def calcular_nomina_completa(
            empleado: Empleado,
            horas_trabajadas: Decimal = Decimal("0"),
            horas_extras: Decimal = Decimal("0"),
            ventas_realizadas: Decimal = Decimal("0")
    ) -> Dict:
        """
        Calcula la nómina completa de un empleado.

        Returns:
            Diccionario con todos los cálculos
        """
        # 1. Calcular salario bruto
        salario_bruto = CalculadoraNomina.calcular_salario_bruto(
            empleado,
            horas_trabajadas,
            horas_extras,
            ventas_realizadas
        )

        # 2. Calcular bonos
        total_bonos, detalles_bonos = CalculadoraNomina.calcular_bonos(
            empleado,
            ventas_realizadas
        )

        # 3. Calcular beneficios
        total_beneficios, detalles_beneficios = CalculadoraNomina.calcular_beneficios(
            empleado
        )

        # 4. Calcular deducciones
        total_deducciones, detalles_deducciones = CalculadoraNomina.calcular_deducciones(
            empleado,
            salario_bruto
        )

        # 5. Calcular salario neto
        salario_neto = (
                salario_bruto +
                total_bonos +
                total_beneficios -
                total_deducciones
        )

        # Validar que el salario neto no sea negativo
        if salario_neto < 0:
            from app.utils.exceptions import SalarioNegativoException
            raise SalarioNegativoException(float(salario_neto), empleado.id_empleado)

        return {
            "salario_bruto": salario_bruto,
            "total_bonos": total_bonos,
            "total_beneficios": total_beneficios,
            "total_deducciones": total_deducciones,
            "salario_neto": salario_neto,
            "detalles_bonos": detalles_bonos,
            "detalles_beneficios": detalles_beneficios,
            "detalles_deducciones": detalles_deducciones
        }