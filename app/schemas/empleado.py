"""
Schemas Pydantic para Empleado.
Define la estructura de datos para empleados.
"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

from app.utils.enums import EstadoEmpleadoEnum, TipoEmpleadoEnum


# Schema base
class EmpleadoBase(BaseModel):
    """Schema base para Empleado."""

    numero_identificacion: str = Field(
        ...,
        min_length=5,
        max_length=20,
        description="Número de identificación único",
        examples=["1001234567"]
    )

    nombres: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombres del empleado",
        examples=["Carlos Alberto"]
    )

    apellidos: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Apellidos del empleado",
        examples=["Rodríguez Pérez"]
    )

    email: Optional[EmailStr] = Field(
        None,
        description="Correo electrónico",
        examples=["carlos.rodriguez@empresa.com"]
    )

    telefono: Optional[str] = Field(
        None,
        max_length=20,
        description="Número telefónico",
        examples=["3101234567"]
    )

    fecha_ingreso: date = Field(
        ...,
        description="Fecha de ingreso a la empresa",
        examples=["2020-01-15"]
    )

    estado: EstadoEmpleadoEnum = Field(
        default=EstadoEmpleadoEnum.ACTIVO,
        description="Estado del empleado"
    )


# Schema para crear
class EmpleadoCreate(EmpleadoBase):
    """Schema para crear un empleado."""

    id_tipo_empleado: int = Field(
        ...,
        gt=0,
        description="ID del tipo de empleado"
    )

    # Campos específicos según tipo
    salario_base: Optional[Decimal] = Field(
        default=None,
        ge=0,
        description="Salario base mensual (para ASALARIADO, COMISION, TEMPORAL)"
    )

    tarifa_hora: Optional[Decimal] = Field(
        default=None,
        ge=0,
        description="Tarifa por hora (para POR_HORAS)"
    )

    porcentaje_comision: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100,
        description="Porcentaje de comisión (para POR_COMISION)"
    )

    acepta_fondo_ahorro: bool = Field(
        default=False,
        description="Si acepta fondo de ahorro"
    )

    fecha_fin_contrato: Optional[date] = Field(
        None,
        description="Fecha fin de contrato (para TEMPORAL)"
    )

    @field_validator('fecha_ingreso')
    @classmethod
    def validar_fecha_ingreso(cls, v: date) -> date:
        """Valida que la fecha de ingreso no sea futura."""
        if v > date.today():
            raise ValueError("La fecha de ingreso no puede ser futura")
        return v

    @field_validator('fecha_fin_contrato')
    @classmethod
    def validar_fecha_fin_contrato(cls, v: Optional[date], info) -> Optional[date]:
        """Valida que la fecha fin sea posterior a la fecha de ingreso."""
        if v is not None:
            fecha_ingreso = info.data.get('fecha_ingreso')
            if fecha_ingreso and v <= fecha_ingreso:
                raise ValueError("La fecha fin debe ser posterior a la fecha de ingreso")
        return v


# Schema para actualizar
class EmpleadoUpdate(BaseModel):
    """Schema para actualizar un empleado."""

    nombres: Optional[str] = Field(None, min_length=1, max_length=100)
    apellidos: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=20)
    estado: Optional[EstadoEmpleadoEnum] = None
    salario_base: Optional[Decimal] = Field(None, ge=0)
    tarifa_hora: Optional[Decimal] = Field(None, ge=0)
    porcentaje_comision: Optional[Decimal] = Field(None, ge=0, le=100)
    acepta_fondo_ahorro: Optional[bool] = None
    fecha_fin_contrato: Optional[date] = None
    fecha_salida: Optional[date] = None


# Schema para respuesta simple
class EmpleadoResponse(EmpleadoBase):
    """Schema para respuesta de empleado."""

    id_empleado: int
    id_tipo_empleado: int
    salario_base: Optional[Decimal] = None
    tarifa_hora: Optional[Decimal] = None
    porcentaje_comision: Optional[Decimal] = None
    acepta_fondo_ahorro: bool
    fecha_fin_contrato: Optional[date] = None
    fecha_salida: Optional[date] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    model_config = ConfigDict(from_attributes=True)


# Schema con información del tipo de empleado
class EmpleadoDetallado(EmpleadoResponse):
    """Schema detallado con información adicional."""

    tipo_empleado_nombre: str = Field(
        ...,
        description="Nombre del tipo de empleado"
    )

    nombre_completo: str = Field(
        ...,
        description="Nombre completo del empleado"
    )

    anios_antiguedad: int = Field(
        default=0,
        description="anios de antigüedad en la empresa"
    )


# Schema para listado (más ligero)
class EmpleadoListado(BaseModel):
    """Schema ligero para listados."""

    id_empleado: int
    numero_identificacion: str
    nombre_completo: str
    email: Optional[str] = None
    tipo_empleado_nombre: str
    estado: EstadoEmpleadoEnum
    fecha_ingreso: date

    model_config = ConfigDict(from_attributes=True)