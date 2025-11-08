"""
Modelo de Empleado.
Representa a un empleado en el sistema con toda su información laboral.
"""

from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Numeric,
    Boolean, Enum as SQLEnum, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base
from app.utils.enums import EstadoEmpleadoEnum


class Empleado(Base):
    """
    Modelo de Empleado.

    Principios SOLID aplicados:
    - Single Responsibility: Solo maneja datos de empleado
    - Open/Closed: Extensible mediante herencia si se necesitan tipos especiales

    Atributos:
        id_empleado: Identificador único
        numero_identificacion: Cédula o documento
        nombres: Nombres del empleado
        apellidos: Apellidos del empleado
        email: Correo electrónico
        telefono: Número telefónico
        id_tipo_empleado: FK a tipo de empleado
        fecha_ingreso: Fecha de ingreso a la empresa
        fecha_salida: Fecha de salida (si aplica)
        estado: Estado actual (ACTIVO, INACTIVO, SUSPENDIDO)
        salario_base: Salario base mensual
        tarifa_hora: Tarifa por hora (solo para POR_HORAS)
        porcentaje_comision: Porcentaje de comisión (solo para POR_COMISION)
        acepta_fondo_ahorro: Flag para fondo de ahorro
        fecha_fin_contrato: Fecha fin de contrato (solo TEMPORAL)
    """

    __tablename__ = "empleado"

    # Columnas principales
    id_empleado = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    numero_identificacion = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True, index=True)
    telefono = Column(String(20), nullable=True)

    # Relación con tipo de empleado
    id_tipo_empleado = Column(
        Integer,
        ForeignKey("tipo_empleado.id_tipo_empleado"),
        nullable=False,
        index=True
    )

    # Información laboral
    fecha_ingreso = Column(Date, nullable=False, index=True)
    fecha_salida = Column(Date, nullable=True)

    estado = Column(
        SQLEnum(EstadoEmpleadoEnum),
        default=EstadoEmpleadoEnum.ACTIVO,
        nullable=False,
        index=True
    )

    # Información salarial (varía según tipo)
    salario_base = Column(Numeric(12, 2), default=0.00)
    tarifa_hora = Column(Numeric(10, 2), default=0.00)
    porcentaje_comision = Column(Numeric(5, 2), default=0.00)

    # Información adicional
    acepta_fondo_ahorro = Column(Boolean, default=False)
    fecha_fin_contrato = Column(Date, nullable=True)

    # Auditoría
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relaciones
    tipo_empleado = relationship("TipoEmpleado", back_populates="empleados")
    nominas = relationship(
        "Nomina",
        back_populates="empleado",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint('salario_base >= 0', name='chk_salario_base'),
        CheckConstraint('tarifa_hora >= 0', name='chk_tarifa_hora'),
        CheckConstraint(
            'porcentaje_comision >= 0 AND porcentaje_comision <= 100',
            name='chk_porcentaje_comision'
        ),
    )

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del empleado."""
        return f"{self.nombres} {self.apellidos}"

    @property
    def esta_activo(self) -> bool:
        """Verifica si el empleado está activo."""
        return self.estado == EstadoEmpleadoEnum.ACTIVO

    def __repr__(self) -> str:
        return f"<Empleado(id={self.id_empleado}, nombre='{self.nombre_completo}')>"

    def __str__(self) -> str:
        return self.nombre_completo