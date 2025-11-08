"""
Modelo de Detalle de Beneficio.
Representa los beneficios aplicados a una nómina.
"""

from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class DetalleBeneficio(Base):
    """
    Modelo de Detalle de Beneficio.

    Registra cada beneficio individual aplicado a una nómina.

    Atributos:
        id_detalle_beneficio: Identificador único
        id_nomina: FK a nómina
        tipo_beneficio: Tipo de beneficio (BONO_ALIMENTACION, FONDO_AHORRO, etc.)
        descripcion: Descripción detallada del beneficio
        monto: Valor monetario del beneficio
        fecha_creacion: Timestamp de creación

    Relaciones:
        nomina: Nómina a la que pertenece el beneficio
    """

    __tablename__ = "detalle_beneficio"

    id_detalle_beneficio = Column(
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

    tipo_beneficio = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Tipo de beneficio: BONO_ALIMENTACION, FONDO_AHORRO, etc."
    )

    descripcion = Column(
        Text,
        nullable=True,
        comment="Descripción detallada del beneficio"
    )

    monto = Column(
        Numeric(12, 2),
        nullable=False,
        comment="Valor monetario del beneficio"
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones
    nomina = relationship("Nomina", back_populates="beneficios")

    # Constraints
    __table_args__ = (
        CheckConstraint('monto >= 0', name='chk_monto_beneficio'),
    )

    def __repr__(self) -> str:
        return f"<DetalleBeneficio(id={self.id_detalle_beneficio}, tipo='{self.tipo_beneficio}', monto={self.monto})>"

    def __str__(self) -> str:
        return f"{self.tipo_beneficio}: ${self.monto:,.2f}"