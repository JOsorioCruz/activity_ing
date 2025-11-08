"""
Schemas Pydantic para Nómina.
Define la estructura completa de nómina con bonos, beneficios y deducciones.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from app.schemas.empleado import EmpleadoListado
from app.schemas.periodo_nomina import PeriodoNominaResponse


# ==========================================
# SCHEMAS PARA DETALLES
# ==========================================

class DetalleBonoBase(BaseModel):
    """Schema base para bono."""
    tipo_bono: str = Field(..., description="Tipo de bono")
    descripcion: Optional[str] = Field(None, description="Descripción del bono")
    monto: Decimal = Field(..., ge=0, description="Monto del bono")
    porcentaje_aplicado: Optional[Decimal] = Field(None, description="Porcentaje aplicado")


class DetalleBonoResponse(DetalleBonoBase):
    """Schema de respuesta para bono."""
    id_detalle_bono: int
    id_nomina: int
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


class DetalleBeneficioBase(BaseModel):
    """Schema base para beneficio."""
    tipo_beneficio: str = Field(..., description="Tipo de beneficio")
    descripcion: Optional[str] = Field(None, description="Descripción del beneficio")
    monto: Decimal = Field(..., ge=0, description="Monto del beneficio")


class DetalleBeneficioResponse(DetalleBeneficioBase):
    """Schema de respuesta para beneficio."""
    id_detalle_beneficio: int
    id_nomina: int
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


class DetalleDeduccionBase(BaseModel):
    """Schema base para deducción."""
    tipo_deduccion: str = Field(..., description="Tipo de deducción")
    descripcion: Optional[str] = Field(None, description="Descripción de la deducción")
    monto: Decimal = Field(..., ge=0, description="Monto de la deducción")
    porcentaje_aplicado: Optional[Decimal] = Field(None, description="Porcentaje aplicado")
    base_calculo: Optional[Decimal] = Field(None, description="Base de cálculo")


class DetalleDeduccionResponse(DetalleDeduccionBase):
    """Schema de respuesta para deducción."""
    id_detalle_deduccion: int
    id_nomina: int
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# SCHEMAS PARA NÓMINA
# ==========================================

class NominaBase(BaseModel):
    """Schema base para nómina."""

    horas_trabajadas: Optional[Decimal] = Field(
        default=0,
        ge=0,
        description="Horas trabajadas (para empleados por horas)"
    )

    horas_extras: Optional[Decimal] = Field(
        default=0,
        ge=0,
        description="Horas extras (para empleados por horas)"
    )

    ventas_realizadas: Optional[Decimal] = Field(
        default=0,
        ge=0,
        description="Ventas realizadas (para empleados por comisión)"
    )


class NominaCreate(NominaBase):
    """
    Schema para crear nómina.
    Solo requiere datos de entrada, el cálculo se hace automáticamente.
    """

    id_empleado: int = Field(..., gt=0, description="ID del empleado")
    id_periodo: int = Field(..., gt=0, description="ID del período")

    @field_validator('horas_trabajadas', 'horas_extras', 'ventas_realizadas')
    @classmethod
    def validar_no_negativo(cls, v: Optional[Decimal]) -> Decimal:
        """Valida que los valores no sean negativos."""
        if v is not None and v < 0:
            raise ValueError("El valor no puede ser negativo")
        return v or Decimal(0)


class NominaUpdate(BaseModel):
    """Schema para actualizar datos de entrada de nómina."""

    horas_trabajadas: Optional[Decimal] = Field(None, ge=0)
    horas_extras: Optional[Decimal] = Field(None, ge=0)
    ventas_realizadas: Optional[Decimal] = Field(None, ge=0)


class NominaResponse(NominaBase):
    """Schema de respuesta básica de nómina."""

    id_nomina: int
    id_empleado: int
    id_periodo: int

    salario_bruto: Decimal = Field(..., description="Salario bruto")
    total_bonos: Decimal = Field(..., description="Total de bonos")
    total_beneficios: Decimal = Field(..., description="Total de beneficios")
    total_deducciones: Decimal = Field(..., description="Total de deducciones")
    salario_neto: Decimal = Field(..., description="Salario neto a pagar")

    calculado_por: Optional[str] = None
    fecha_calculo: datetime

    model_config = ConfigDict(from_attributes=True)


class NominaDetallada(NominaResponse):
    """
    Schema detallado de nómina con todos los detalles.
    Incluye listas de bonos, beneficios y deducciones.
    """

    # Información relacionada
    empleado: EmpleadoListado
    periodo: PeriodoNominaResponse

    # Detalles
    bonos: List[DetalleBonoResponse] = Field(default_factory=list)
    beneficios: List[DetalleBeneficioResponse] = Field(default_factory=list)
    deducciones: List[DetalleDeduccionResponse] = Field(default_factory=list)

    # Campos calculados
    total_ingresos: Decimal = Field(
        ...,
        description="Total de ingresos (bruto + bonos + beneficios)"
    )

    porcentaje_deducciones: float = Field(
        ...,
        description="Porcentaje de deducciones sobre salario bruto"
    )


class NominaResumen(BaseModel):
    """Schema resumido para listados."""

    id_nomina: int
    empleado_nombre: str
    empleado_identificacion: str
    periodo_texto: str
    salario_bruto: Decimal
    salario_neto: Decimal
    fecha_calculo: datetime

    model_config = ConfigDict(from_attributes=True)


class NominaCalculoRequest(BaseModel):
    """Request para calcular nómina de múltiples empleados."""

    id_periodo: int = Field(..., gt=0, description="ID del período")
    empleados: List[NominaCreate] = Field(
        ...,
        min_length=1,
        description="Lista de datos de empleados para calcular"
    )


class NominaCalculoResponse(BaseModel):
    """Response del cálculo de múltiples nóminas."""

    periodo_id: int
    total_nominas_calculadas: int
    total_nominas_fallidas: int
    nominas_exitosas: List[NominaResponse]
    errores: List[dict] = Field(default_factory=list)