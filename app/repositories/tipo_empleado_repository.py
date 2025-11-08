"""
Repository para Tipo de Empleado.
Extiende BaseRepository con operaciones específicas.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.base_repository import BaseRepository
from app.models.tipo_empleado import TipoEmpleado


class TipoEmpleadoRepository(BaseRepository[TipoEmpleado]):
    """Repository para Tipo de Empleado."""

    def __init__(self, db: Session):
        super().__init__(TipoEmpleado, db)

    def get_by_id(self, id: int) -> Optional[TipoEmpleado]:
        """
        Obtiene tipo de empleado por ID.
        Sobrescribe método base para usar el campo correcto.
        """
        return self.db.query(self.model).filter(
            self.model.id_tipo_empleado == id
        ).first()

    def get_by_nombre(self, nombre_tipo: str) -> Optional[TipoEmpleado]:
        """
        Obtiene tipo de empleado por nombre.

        Args:
            nombre_tipo: Nombre del tipo

        Returns:
            TipoEmpleado o None
        """
        return self.db.query(self.model).filter(
            self.model.nombre_tipo == nombre_tipo
        ).first()

    def exists_by_nombre(self, nombre_tipo: str) -> bool:
        """
        Verifica si existe un tipo con ese nombre.

        Args:
            nombre_tipo: Nombre del tipo

        Returns:
            True si existe
        """
        return self.db.query(self.model).filter(
            self.model.nombre_tipo == nombre_tipo
        ).first() is not None

    def delete(self, id: int) -> bool:
        """Elimina tipo de empleado por ID."""
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False