"""
Servicio de Empleado.
Maneja la lógica de negocio relacionada con empleados.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.empleado import Empleado
from app.repositories.empleado_repository import EmpleadoRepository
from app.repositories.tipo_empleado_repository import TipoEmpleadoRepository

from app.schemas.empleado import EmpleadoCreate, EmpleadoUpdate

from app.utils.exceptions import (
    EmpleadoNoEncontradoException,
    NominaException
)


class EmpleadoService:
    """Servicio para gestión de empleados."""

    def __init__(self, db: Session):
        self.db = db
        self.empleado_repo = EmpleadoRepository(db)
        self.tipo_empleado_repo = TipoEmpleadoRepository(db)

    def crear_empleado(self, empleado_data: EmpleadoCreate) -> Empleado:
        """
        Crea un nuevo empleado.

        Args:
            empleado_data: Datos del empleado a crear

        Returns:
            Empleado creado

        Raises:
            NominaException: Si hay errores de validación
        """
        # Validar que no exista otro empleado con esa identificación
        if self.empleado_repo.get_by_identificacion(empleado_data.numero_identificacion):
            raise NominaException(
                message=f"Ya existe un empleado con identificación {empleado_data.numero_identificacion}",
                code="IDENTIFICACION_DUPLICADA"
            )

        # Validar que no exista otro empleado con ese email
        if empleado_data.email and self.empleado_repo.get_by_email(empleado_data.email):
            raise NominaException(
                message=f"Ya existe un empleado con email {empleado_data.email}",
                code="EMAIL_DUPLICADO"
            )

        # Validar que el tipo de empleado exista
        tipo_empleado = self.tipo_empleado_repo.get_by_id(empleado_data.id_tipo_empleado)
        if not tipo_empleado:
            raise NominaException(
                message=f"Tipo de empleado con ID {empleado_data.id_tipo_empleado} no encontrado",
                code="TIPO_EMPLEADO_NOT_FOUND"
            )

        # Crear empleado
        empleado = Empleado(**empleado_data.model_dump())
        return self.empleado_repo.create(empleado)

    def obtener_empleado(self, id_empleado: int) -> Empleado:
        """
        Obtiene un empleado por ID.

        Args:
            id_empleado: ID del empleado

        Returns:
            Empleado encontrado

        Raises:
            EmpleadoNoEncontradoException: Si no existe
        """
        empleado = self.empleado_repo.get_by_id(id_empleado)
        if not empleado:
            raise EmpleadoNoEncontradoException(id_empleado)
        return empleado

    def listar_empleados(
            self,
            skip: int = 0,
            limit: int = 100,
            solo_activos: bool = False
    ) -> List[Empleado]:
        """
        Lista empleados con paginación.

        Args:
            skip: Registros a saltar
            limit: Límite de registros
            solo_activos: Si solo mostrar activos

        Returns:
            Lista de empleados
        """
        if solo_activos:
            return self.empleado_repo.get_all_activos(skip, limit)
        return self.empleado_repo.get_all(skip, limit)

    def buscar_empleados(self, termino: str, skip: int = 0, limit: int = 100) -> List[Empleado]:
        """
        Busca empleados por término.

        Args:
            termino: Término de búsqueda
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de empleados que coinciden
        """
        return self.empleado_repo.buscar(termino, skip, limit)

    def actualizar_empleado(
            self,
            id_empleado: int,
            empleado_update: EmpleadoUpdate
    ) -> Empleado:
        """
        Actualiza un empleado.

        Args:
            id_empleado: ID del empleado
            empleado_update: Datos a actualizar

        Returns:
            Empleado actualizado
        """
        empleado = self.obtener_empleado(id_empleado)

        # Validar email único si se está actualizando
        if empleado_update.email:
            empleado_email = self.empleado_repo.get_by_email(empleado_update.email)
            if empleado_email and empleado_email.id_empleado != id_empleado:
                raise NominaException(
                    message=f"El email {empleado_update.email} ya está en uso",
                    code="EMAIL_DUPLICADO"
                )

        # Actualizar campos
        update_data = empleado_update.model_dump(exclude_unset=True)
        return self.empleado_repo.update(empleado, update_data)

    def eliminar_empleado(self, id_empleado: int) -> bool:
        """
        Elimina un empleado.

        Args:
            id_empleado: ID del empleado

        Returns:
            True si se eliminó
        """
        empleado = self.obtener_empleado(id_empleado)
        return self.empleado_repo.delete(id_empleado)

    def obtener_empleados_con_antiguedad(
            self,
            anios_minimos: int
    ) -> List[Empleado]:
        """
        Obtiene empleados con X anios de antigüedad mínimos.

        Args:
            anios_minimos: anios mínimos de antigüedad

        Returns:
            Lista de empleados
        """
        return self.empleado_repo.get_con_antiguedad_mayor_a(anios_minimos)