"""
Modelo de Tipo de Empleado.
Representa los diferentes tipos de empleado en el sistema.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class TipoEmpleado(Base):
    """
    Modelo de Tipo de Empleado.

    Atributos:
        id_tipo_empleado: Identificador único
        nombre_tipo: Nombre del tipo (ASALARIADO, POR_HORAS, etc.)
        descripcion: Descripción detallada del tipo
        fecha_creacion: Timestamp de creación

    Relaciones:
        empleados: Lista de empleados de este tipo
    """

    __tablename__ = "tipo_empleado"

    # Columnas
    id_tipo_empleado = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Identificador único del tipo de empleado"
    )

    nombre_tipo = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Nombre del tipo: ASALARIADO, POR_HORAS, POR_COMISION, TEMPORAL"
    )

    descripcion = Column(
        Text,
        nullable=True,
        comment="Descripción detallada del tipo de empleado"
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Fecha y hora de creación del registro"
    )

    # Relaciones
    empleados = relationship(
        "Empleado",
        back_populates="tipo_empleado",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Representación en string del objeto."""
        return f"<TipoEmpleado(id={self.id_tipo_empleado}, nombre='{self.nombre_tipo}')>"

    def __str__(self) -> str:
        """String legible del objeto."""
        return self.nombre_tipo