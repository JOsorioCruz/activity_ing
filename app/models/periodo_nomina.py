"""
Modelo de Período de Nómina.
Representa los períodos mensuales para cálculo de nómina.
"""

from sqlalchemy import (
    Column, Integer, Date, DateTime, Enum as SQLEnum,
    CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base
from app.utils.enums import EstadoPeriodoEnum


class PeriodoNomina(Base):
    """
    Modelo de Período de Nómina.

    Atributos:
        id_periodo: Identificador único
        año: Año del período
        mes: Mes del período (1-12)
        fecha_inicio: Fecha de inicio del período
        fecha_fin: Fecha de fin del período
        fecha_pago: Fecha programada de pago
        estado: Estado del período
    """

    __tablename__ = "periodo_nomina"

    id_periodo = Column(Integer, primary_key=True, index=True, autoincrement=True)
    anio = Column(Integer, nullable=False, index=True)
    mes = Column(Integer, nullable=False, index=True)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    fecha_pago = Column(Date, nullable=False)

    estado = Column(
        SQLEnum(EstadoPeriodoEnum),
        default=EstadoPeriodoEnum.ABIERTO,
        nullable=False,
        index=True
    )

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    nominas = relationship(
        "Nomina",
        back_populates="periodo",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint('mes BETWEEN 1 AND 12', name='chk_mes'),
        UniqueConstraint('anio', 'mes', name='uk_periodo'),
    )

    @property
    def periodo_texto(self) -> str:
        """Retorna el período en formato texto."""
        return f"{self.anio}-{self.mes:02d}"

    @property
    def esta_cerrado(self) -> bool:
        """Verifica si el período está cerrado."""
        return self.estado in [EstadoPeriodoEnum.CERRADO, EstadoPeriodoEnum.PAGADO]

    def __repr__(self) -> str:
        return f"<PeriodoNomina(id={self.id_periodo}, periodo='{self.periodo_texto}')>"