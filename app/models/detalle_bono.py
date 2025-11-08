"""
Modelo de Detalle de Bono.
Representa los bonos aplicados a una nómina.
"""

from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class DetalleBono(Base):
    """
    Modelo de Detalle de Bono.

    Registra cada bono individual aplicado a una nómina.

    Atributos:
        id_detalle_bono: Identificador único
        id_nomina: FK a nómina
        tipo_bono: Tipo de bono (BONO_ANTIGUEDAD, BONO_VENTAS, etc.)
        descripcion: Descripción detallada del bono
        monto: Valor monetario del bono
        porcentaje_aplicado: Porcentaje usado para calcular el bono
        fecha_creacion: Timestamp de creación

    Relaciones:
        nomina: Nómina a la que pertenece el bono
    """

    __tablename__ = "detalle_bono"

    id_detalle_bono = Column(
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

    tipo_bono = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Tipo de bono: BONO_ANTIGUEDAD, BONO_VENTAS, etc."
    )

    descripcion = Column(
        Text,
        nullable=True,
        comment="Descripción detallada del bono"
    )

    monto = Column(
        Numeric(12, 2),
        nullable=False,
        comment="Valor monetario del bono"
    )

    porcentaje_aplicado = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Porcentaje usado para calcular el bono"
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relaciones
    nomina = relationship("Nomina", back_populates="bonos")

    # Constraints
    __table_args__ = (
        CheckConstraint('monto >= 0', name='chk_monto_bono'),
    )

    def __repr__(self) -> str:
        return f"<DetalleBono(id={self.id_detalle_bono}, tipo='{self.tipo_bono}', monto={self.monto})>"

    def __str__(self) -> str:
        return f"{self.tipo_bono}: ${self.monto:,.2f}"