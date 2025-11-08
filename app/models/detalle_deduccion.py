"""
Modelo de Detalle de Deducción.
Representa las deducciones aplicadas a una nómina.
"""

from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class DetalleDeduccion(Base):
    """
    Modelo de Detalle de Deducción.

    Registra cada deducción individual aplicada a una nómina.

    Atributos:
        id_detalle_deduccion: Identificador único
        id_nomina: FK a nómina
        tipo_deduccion: Tipo de deducción (SEGURIDAD_SOCIAL_PENSION, ARL, etc.)
        descripcion: Descripción detallada de la deducción
        monto: Valor monetario de la deducción
        porcentaje_aplicado: Porcentaje usado para calcular la deducción
        base_calculo: Monto sobre el cual se calculó la deducción
        fecha_creacion: Timestamp de creación

    Relaciones:
        nomina: Nómina a la que pertenece la deducción
    """

    __tablename__ = "detalle_deduccion"

    id_detalle_deduccion = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    id_nomina = Column(
        Integer,
        ForeignKey("nomina.id_nomina", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    tipo_deduccion = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Tipo: SEGURIDAD_SOCIAL_PENSION, ARL, FONDO_AHORRO_EMPLEADO"
    )

    descripcion = Column(
        Text,
        nullable=True,
        comment="Descripción detallada de la deducción"
    )

    monto = Column(
        Numeric(12, 2),
        nullable=False,
        comment="Valor monetario de la deducción"
    )

    porcentaje_aplicado = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Porcentaje usado para calcular la deducción"
    )

    base_calculo = Column(
        Numeric(12, 2),
        nullable=True,
        comment="Monto sobre el cual se calculó la deducción"
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones
    nomina = relationship("Nomina", back_populates="deducciones")

    # Constraints
    __table_args__ = (
        CheckConstraint('monto >= 0', name='chk_monto_deduccion'),
    )

    def __repr__(self) -> str:
        return f"<DetalleDeduccion(id={self.id_detalle_deduccion}, tipo='{self.tipo_deduccion}', monto={self.monto})>"

    def __str__(self) -> str:
        return f"{self.tipo_deduccion}: ${self.monto:,.2f}"