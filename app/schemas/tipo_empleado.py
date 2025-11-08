"""
Schemas Pydantic para Tipo de Empleado.
Define la estructura de datos para API requests/responses.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


# Schema base con campos comunes
class TipoEmpleadoBase(BaseModel):
    """Schema base para Tipo de Empleado."""

    nombre_tipo: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Nombre del tipo de empleado",
        examples=["ASALARIADO"]
    )

    descripcion: Optional[str] = Field(
        None,
        description="Descripción del tipo de empleado",
        examples=["Empleado con salario fijo mensual"]
    )


# Schema para crear (sin id, sin fecha_creacion)
class TipoEmpleadoCreate(TipoEmpleadoBase):
    """Schema para crear un tipo de empleado."""
    pass


# Schema para actualizar (todos los campos opcionales)
class TipoEmpleadoUpdate(BaseModel):
    """Schema para actualizar un tipo de empleado."""

    nombre_tipo: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50
    )

    descripcion: Optional[str] = None


# Schema para respuesta (incluye todos los campos)
class TipoEmpleadoResponse(TipoEmpleadoBase):
    """Schema para respuesta de tipo de empleado."""

    id_tipo_empleado: int = Field(..., description="ID único del tipo de empleado")
    fecha_creacion: datetime = Field(..., description="Fecha de creación")

    # Configuración para trabajar con modelos ORM
    model_config = ConfigDict(from_attributes=True)


# Schema con información adicional (ej: cantidad de empleados)
class TipoEmpleadoDetallado(TipoEmpleadoResponse):
    """Schema detallado con información adicional."""

    cantidad_empleados: int = Field(
        default=0,
        description="Cantidad de empleados de este tipo"
    )