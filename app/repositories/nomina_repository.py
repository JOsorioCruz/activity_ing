"""
Repository para Nómina.
"""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.repositories.base_repository import BaseRepository
from app.models.nomina import Nomina
from app.models.detalle_bono import DetalleBono
from app.models.detalle_beneficio import DetalleBeneficio
from app.models.detalle_deduccion import DetalleDeduccion


class NominaRepository(BaseRepository[Nomina]):
    """Repository para Nómina."""

    def __init__(self, db: Session):
        super().__init__(Nomina, db)

    def get_by_id(self, id: int) -> Optional[Nomina]:
        """
        Obtiene nómina por ID con todas las relaciones cargadas.
        """
        return self.db.query(self.model).options(
            joinedload(self.model.empleado),
            joinedload(self.model.periodo),
            joinedload(self.model.bonos),
            joinedload(self.model.beneficios),
            joinedload(self.model.deducciones)
        ).filter(
            self.model.id_nomina == id
        ).first()

    def get_by_empleado_periodo(
            self,
            id_empleado: int,
            id_periodo: int
    ) -> Optional[Nomina]:
        """
        Obtiene nómina por empleado y período.

        Args:
            id_empleado: ID del empleado
            id_periodo: ID del período

        Returns:
            Nomina o None
        """
        return self.db.query(self.model).filter(
            and_(
                self.model.id_empleado == id_empleado,
                self.model.id_periodo == id_periodo
            )
        ).first()

    def get_by_empleado(
            self,
            id_empleado: int,
            skip: int = 0,
            limit: int = 100
    ) -> List[Nomina]:
        """
        Obtiene todas las nóminas de un empleado.

        Args:
            id_empleado: ID del empleado
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de nóminas
        """
        return self.db.query(self.model).options(
            joinedload(self.model.periodo)
        ).filter(
            self.model.id_empleado == id_empleado
        ).order_by(
            self.model.fecha_calculo.desc()
        ).offset(skip).limit(limit).all()

    def get_by_periodo(
            self,
            id_periodo: int,
            skip: int = 0,
            limit: int = 100
    ) -> List[Nomina]:
        """
        Obtiene todas las nóminas de un período.

        Args:
            id_periodo: ID del período
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de nóminas
        """
        return self.db.query(self.model).options(
            joinedload(self.model.empleado)
        ).filter(
            self.model.id_periodo == id_periodo
        ).offset(skip).limit(limit).all()

    def exists_nomina(self, id_empleado: int, id_periodo: int) -> bool:
        """
        Verifica si existe nómina para empleado/período.

        Args:
            id_empleado: ID del empleado
            id_periodo: ID del período

        Returns:
            True si existe
        """
        return self.get_by_empleado_periodo(id_empleado, id_periodo) is not None

    def count_by_periodo(self, id_periodo: int) -> int:
        """
        Cuenta nóminas de un período.

        Args:
            id_periodo: ID del período

        Returns:
            Cantidad de nóminas
        """
        return self.db.query(self.model).filter(
            self.model.id_periodo == id_periodo
        ).count()

    def delete(self, id: int) -> bool:
        """Elimina nómina por ID."""
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False