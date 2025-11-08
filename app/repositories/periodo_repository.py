"""
Repository para Período de Nómina.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.repositories.base_repository import BaseRepository
from app.models.periodo_nomina import PeriodoNomina
from app.utils.enums import EstadoPeriodoEnum


class PeriodoNominaRepository(BaseRepository[PeriodoNomina]):
    """Repository para Período de Nómina."""

    def __init__(self, db: Session):
        super().__init__(PeriodoNomina, db)

    def get_by_id(self, id: int) -> Optional[PeriodoNomina]:
        """Obtiene período por ID."""
        return self.db.query(self.model).filter(
            self.model.id_periodo == id
        ).first()

    def get_by_anio_mes(self, anio: int, mes: int) -> Optional[PeriodoNomina]:
        """
        Obtiene período por anio y mes.

        Args:
            anio: anio del período
            mes: Mes del período

        Returns:
            PeriodoNomina o None
        """
        return self.db.query(self.model).filter(
            and_(
                self.model.anio == anio,
                self.model.mes == mes
            )
        ).first()

    def get_by_estado(
            self,
            estado: EstadoPeriodoEnum,
            skip: int = 0,
            limit: int = 100
    ) -> List[PeriodoNomina]:
        """
        Obtiene períodos por estado.

        Args:
            estado: Estado del período
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de períodos
        """
        return self.db.query(self.model).filter(
            self.model.estado == estado
        ).offset(skip).limit(limit).all()

    def get_abiertos(self) -> List[PeriodoNomina]:
        """Obtiene períodos abiertos."""
        return self.get_by_estado(EstadoPeriodoEnum.ABIERTO)

    def exists_periodo(self, anio: int, mes: int) -> bool:
        """
        Verifica si existe un período para el anio/mes.

        Args:
            anio: anio
            mes: Mes

        Returns:
            True si existe
        """
        return self.get_by_anio_mes(anio, mes) is not None

    def get_ultimos(self, cantidad: int = 12) -> List[PeriodoNomina]:
        """
        Obtiene los últimos N períodos.

        Args:
            cantidad: Cantidad de períodos

        Returns:
            Lista de períodos ordenados por fecha
        """
        return self.db.query(self.model).order_by(
            self.model.anio.desc(),
            self.model.mes.desc()
        ).limit(cantidad).all()

    def delete(self, id: int) -> bool:
        """Elimina período por ID."""
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False