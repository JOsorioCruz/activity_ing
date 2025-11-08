"""
Modelo de Nómina.
Representa el cálculo de nómina para un empleado en un período específico.
"""

from sqlalchemy import (
    Column, Integer, Numeric, DateTime, ForeignKey,
    CheckConstraint, UniqueConstraint, String
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from decimal import Decimal

from app.db.session import Base


class Nomina(Base):
    """
    Modelo de Nómina.

    Almacena el cálculo completo de nómina para un empleado en un período.

    Atributos:
        id_nomina: Identificador único
        id_empleado: FK a empleado
        id_periodo: FK a período de nómina
        horas_trabajadas: Horas trabajadas (solo para empleados por horas)
        horas_extras: Horas extras (solo para empleados por horas)
        ventas_realizadas: Ventas del período (solo para empleados por comisión)
        salario_bruto: Salario antes de deducciones
        total_bonos: Suma de todos los bonos
        total_beneficios: Suma de todos los beneficios
        total_deducciones: Suma de todas las deducciones
        salario_neto: Salario final a pagar
        calculado_por: Usuario que realizó el cálculo
        fecha_calculo: Timestamp del cálculo

    Relaciones:
        empleado: Empleado al que pertenece la nómina
        periodo: Período de nómina
        bonos: Lista de bonos aplicados
        beneficios: Lista de beneficios aplicados
        deducciones: Lista de deducciones aplicadas
        auditorias: Historial de cambios
    """

    __tablename__ = "nomina"

    # Columnas principales
    id_nomina = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Identificador único de la nómina"
    )

    id_empleado = Column(
        Integer,
        ForeignKey("empleado.id_empleado", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK al empleado"
    )

    id_periodo = Column(
        Integer,
        ForeignKey("periodo_nomina.id_periodo", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK al período de nómina"
    )

    # Datos específicos del período
    horas_trabajadas = Column(
        Numeric(6, 2),
        default=0.00,
        comment="Horas trabajadas (solo para empleados por horas)"
    )

    horas_extras = Column(
        Numeric(6, 2),
        default=0.00,
        comment="Horas extras trabajadas (solo para empleados por horas)"
    )

    ventas_realizadas = Column(
        Numeric(15, 2),
        default=0.00,
        comment="Ventas realizadas (solo para empleados por comisión)"
    )

    # Cálculos de salario
    salario_bruto = Column(
        Numeric(12, 2),
        nullable=False,
        default=0.00,
        comment="Salario bruto antes de deducciones"
    )

    total_bonos = Column(
        Numeric(12, 2),
        default=0.00,
        comment="Total de bonos aplicados"
    )

    total_beneficios = Column(
        Numeric(12, 2),
        default=0.00,
        comment="Total de beneficios aplicados"
    )

    total_deducciones = Column(
        Numeric(12, 2),
        default=0.00,
        comment="Total de deducciones aplicadas"
    )

    salario_neto = Column(
        Numeric(12, 2),
        nullable=False,
        default=0.00,
        comment="Salario neto a pagar"
    )

    # Auditoría
    calculado_por = Column(
        String(100),
        nullable=True,
        comment="Usuario que realizó el cálculo"
    )

    fecha_calculo = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Fecha y hora del cálculo"
    )

    # Relaciones
    empleado = relationship("Empleado", back_populates="nominas")
    periodo = relationship("PeriodoNomina", back_populates="nominas")

    bonos = relationship(
        "DetalleBono",
        back_populates="nomina",
        cascade="all, delete-orphan"
    )

    beneficios = relationship(
        "DetalleBeneficio",
        back_populates="nomina",
        cascade="all, delete-orphan"
    )

    deducciones = relationship(
        "DetalleDeduccion",
        back_populates="nomina",
        cascade="all, delete-orphan"
    )

    auditorias = relationship(
        "AuditoriaNomina",
        back_populates="nomina",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        # Un empleado solo puede tener una nómina por período
        UniqueConstraint(
            'id_empleado',
            'id_periodo',
            name='uk_nomina_empleado_periodo'
        ),
        CheckConstraint('horas_trabajadas >= 0', name='chk_horas_trabajadas'),
        CheckConstraint('horas_extras >= 0', name='chk_horas_extras'),
        CheckConstraint('ventas_realizadas >= 0', name='chk_ventas'),
        CheckConstraint('salario_neto >= 0', name='chk_salario_neto'),
    )

    @property
    def total_ingresos(self) -> Decimal:
        """Calcula el total de ingresos (bruto + bonos + beneficios)."""
        return (
                Decimal(str(self.salario_bruto or 0)) +
                Decimal(str(self.total_bonos or 0)) +
                Decimal(str(self.total_beneficios or 0))
        )

    @property
    def porcentaje_deducciones(self) -> float:
        """Calcula el porcentaje de deducciones sobre el salario bruto."""
        if self.salario_bruto and self.salario_bruto > 0:
            return float((self.total_deducciones / self.salario_bruto) * 100)
        return 0.0

    def __repr__(self) -> str:
        return f"<Nomina(id={self.id_nomina}, empleado_id={self.id_empleado}, periodo_id={self.id_periodo})>"

    def __str__(self) -> str:
        return f"Nómina #{self.id_nomina} - Neto: ${self.salario_neto:,.2f}"