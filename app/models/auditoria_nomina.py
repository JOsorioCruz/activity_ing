"""
Modelo de Auditoría de Nómina.
Registra cambios y eventos relacionados con las nóminas.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class AuditoriaNomina(Base):
    """
    Modelo de Auditoría de Nómina.

    Mantiene un historial de cambios en las nóminas para trazabilidad.

    Atributos:
        id_auditoria: Identificador único
        id_nomina: FK a nómina
        accion: Tipo de acción (CREAR, MODIFICAR, CALCULAR, APROBAR, etc.)
        usuario: Usuario que realizó la acción
        descripcion: Descripción de la acción
        valores_anteriores: Valores antes del cambio (JSON)
        valores_nuevos: Valores después del cambio (JSON)
        fecha_accion: Timestamp de la acción

    Relaciones:
        nomina: Nómina auditada
    """

    __tablename__ = "auditoria_nomina"

    id_auditoria = Column(
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

    accion = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Tipo de acción: CREAR, MODIFICAR, CALCULAR, APROBAR, RECHAZAR"
    )

    usuario = Column(
        String(100),
        nullable=True,
        comment="Usuario que realizó la acción"
    )

    descripcion = Column(
        Text,
        nullable=True,
        comment="Descripción detallada de la acción"
    )

    valores_anteriores = Column(
        JSON,
        nullable=True,
        comment="Valores antes del cambio (JSON)"
    )

    valores_nuevos = Column(
        JSON,
        nullable=True,
        comment="Valores después del cambio (JSON)"
    )

    fecha_accion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # Relaciones
    nomina = relationship("Nomina", back_populates="auditorias")

    def __repr__(self) -> str:
        return f"<AuditoriaNomina(id={self.id_auditoria}, accion='{self.accion}', nomina_id={self.id_nomina})>"

    def __str__(self) -> str:
        return f"{self.accion} - {self.fecha_accion.strftime('%Y-%m-%d %H:%M:%S')}"