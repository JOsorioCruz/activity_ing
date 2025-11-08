"""
Repository para Empleado.
Operaciones de acceso a datos para empleados.
"""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from datetime import date

from app.repositories.base_repository import BaseRepository
from app.models.empleado import Empleado
from app.models.tipo_empleado import TipoEmpleado
from app.utils.enums import EstadoEmpleadoEnum, TipoEmpleadoEnum


class EmpleadoRepository(BaseRepository[Empleado]):
    """Repository para Empleado."""

    def __init__(self, db: Session):
        super().__init__(Empleado, db)

    def get_by_id(self, id: int) -> Optional[Empleado]:
        """
        Obtiene empleado por ID con su tipo de empleado.
        """
        return self.db.query(self.model).options(
            joinedload(self.model.tipo_empleado)
        ).filter(
            self.model.id_empleado == id
        ).first()

    def get_by_identificacion(self, numero_identificacion: str) -> Optional[Empleado]:
        """
        Obtiene empleado por número de identificación.

        Args:
            numero_identificacion: Número de identificación

        Returns:
            Empleado o None
        """
        return self.db.query(self.model).filter(
            self.model.numero_identificacion == numero_identificacion
        ).first()

    def get_by_email(self, email: str) -> Optional[Empleado]:
        """
        Obtiene empleado por email.

        Args:
            email: Email del empleado

        Returns:
            Empleado o None
        """
        return self.db.query(self.model).filter(
            self.model.email == email
        ).first()

    def get_all_activos(
            self,
            skip: int = 0,
            limit: int = 100
    ) -> List[Empleado]:
        """
        Obtiene todos los empleados activos.

        Args:
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de empleados activos
        """
        return self.db.query(self.model).options(
            joinedload(self.model.tipo_empleado)
        ).filter(
            self.model.estado == EstadoEmpleadoEnum.ACTIVO
        ).offset(skip).limit(limit).all()

    def get_by_tipo(
            self,
            id_tipo_empleado: int,
            skip: int = 0,
            limit: int = 100
    ) -> List[Empleado]:
        """
        Obtiene empleados por tipo.

        Args:
            id_tipo_empleado: ID del tipo de empleado
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de empleados del tipo especificado
        """
        return self.db.query(self.model).filter(
            self.model.id_tipo_empleado == id_tipo_empleado
        ).offset(skip).limit(limit).all()

    def buscar(
            self,
            termino: str,
            skip: int = 0,
            limit: int = 100
    ) -> List[Empleado]:
        """
        Busca empleados por nombre, apellido o identificación.

        Args:
            termino: Término de búsqueda
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de empleados que coinciden
        """
        termino_like = f"%{termino}%"

        return self.db.query(self.model).options(
            joinedload(self.model.tipo_empleado)
        ).filter(
            or_(
                self.model.nombres.ilike(termino_like),
                self.model.apellidos.ilike(termino_like),
                self.model.numero_identificacion.ilike(termino_like),
                self.model.email.ilike(termino_like)
            )
        ).offset(skip).limit(limit).all()

    def get_con_antiguedad_mayor_a(
            self,
            anios: int,
            tipo_empleado: Optional[TipoEmpleadoEnum] = None
    ) -> List[Empleado]:
        """
        Obtiene empleados con antigüedad mayor a X años.

        Args:
            años: Años de antigüedad mínimos
            tipo_empleado: Filtrar por tipo (opcional)

        Returns:
            Lista de empleados
        """
        fecha_limite = date.today().replace(year=date.today().year - anios)

        query = self.db.query(self.model).filter(
            and_(
                self.model.fecha_ingreso <= fecha_limite,
                self.model.estado == EstadoEmpleadoEnum.ACTIVO
            )
        )

        if tipo_empleado:
            query = query.join(TipoEmpleado).filter(
                TipoEmpleado.nombre_tipo == tipo_empleado.value
            )

        return query.all()

    def count_by_tipo(self, id_tipo_empleado: int) -> int:
        """
        Cuenta empleados de un tipo específico.

        Args:
            id_tipo_empleado: ID del tipo

        Returns:
            Cantidad de empleados
        """
        return self.db.query(self.model).filter(
            self.model.id_tipo_empleado == id_tipo_empleado
        ).count()

    def count_activos(self) -> int:
        """Cuenta empleados activos."""
        return self.db.query(self.model).filter(
            self.model.estado == EstadoEmpleadoEnum.ACTIVO
        ).count()

    def delete(self, id: int) -> bool:
        """Elimina empleado por ID."""
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False