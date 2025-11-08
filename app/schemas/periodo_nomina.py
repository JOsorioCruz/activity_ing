"""
Schemas Pydantic para Período de Nómina.
"""
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import date, datetime
from typing import Optional

from app.utils.enums import EstadoPeriodoEnum


class PeriodoNominaBase(BaseModel):
    """Schema base para Período de Nómina."""

    anio: int = Field(
        ...,
        ge=2000,
        le=2100,
        description="anio del período",
        examples=[2025]
    )

    mes: int = Field(
        ...,
        ge=1,
        le=12,
        description="Mes del período",
        examples=[11]
    )

    fecha_inicio: date = Field(
        ...,
        description="Fecha de inicio del período"
    )

    fecha_fin: date = Field(
        ...,
        description="Fecha de fin del período"
    )

    fecha_pago: date = Field(
        ...,
        description="Fecha programada de pago"
    )

    @field_validator('fecha_fin')
    @classmethod
    def validar_fecha_fin(cls, v: date, info) -> date:
        """Valida que fecha_fin sea posterior a fecha_inicio."""
        fecha_inicio = info.data.get('fecha_inicio')
        if fecha_inicio and v <= fecha_inicio:
            raise ValueError("La fecha fin debe ser posterior a la fecha de inicio")
        return v


class PeriodoNominaCreate(PeriodoNominaBase):
    """Schema para crear período."""

    estado: EstadoPeriodoEnum = Field(
        default=EstadoPeriodoEnum.ABIERTO,
        description="Estado del período"
    )


class PeriodoNominaUpdate(BaseModel):
    """Schema para actualizar período."""

    fecha_pago: Optional[date] = None
    estado: Optional[EstadoPeriodoEnum] = None


class PeriodoNominaResponse(PeriodoNominaBase):
    """Schema para respuesta."""

    id_periodo: int
    estado: EstadoPeriodoEnum
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


class PeriodoNominaDetallado(PeriodoNominaResponse):
    """Schema detallado con estadísticas."""

    cantidad_nominas: int = Field(
        default=0,
        description="Cantidad de nóminas en este período"
    )

    total_nomina: Decimal = Field(
        default=0,
        description="Total a pagar en este período"
    )

    periodo_texto: str = Field(
        ...,
        description="Período en formato texto (YYYY-MM)"
    )