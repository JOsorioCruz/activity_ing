"""
Endpoints para Tipos de Empleado.
Operaciones CRUD básicas.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_database
from app.repositories.tipo_empleado_repository import TipoEmpleadoRepository
from app.models.tipo_empleado import TipoEmpleado
from app.schemas.tipo_empleado import (
    TipoEmpleadoCreate,
    TipoEmpleadoUpdate,
    TipoEmpleadoResponse,
    TipoEmpleadoDetallado
)
from app.utils.exceptions import NominaException

router = APIRouter()


@router.get(
    "/",
    response_model=List[TipoEmpleadoResponse],
    summary="Listar tipos de empleado",
    description="Obtiene todos los tipos de empleado disponibles en el sistema"
)
def listar_tipos_empleado(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_database)
):
    """
    Lista todos los tipos de empleado.

    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a retornar
    """
    repo = TipoEmpleadoRepository(db)
    tipos = repo.get_all(skip=skip, limit=limit)
    return tipos


@router.get(
    "/{id_tipo_empleado}",
    response_model=TipoEmpleadoDetallado,
    summary="Obtener tipo de empleado",
    description="Obtiene un tipo de empleado específico por su ID con información detallada"
)
def obtener_tipo_empleado(
        id_tipo_empleado: int,
        db: Session = Depends(get_database)
):
    """
    Obtiene un tipo de empleado por ID.

    - **id_tipo_empleado**: ID único del tipo de empleado
    """
    repo = TipoEmpleadoRepository(db)
    tipo = repo.get_by_id(id_tipo_empleado)

    if not tipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipo de empleado con ID {id_tipo_empleado} no encontrado"
        )

    # Contar empleados de este tipo
    from app.repositories.empleado_repository import EmpleadoRepository
    empleado_repo = EmpleadoRepository(db)
    cantidad_empleados = empleado_repo.count_by_tipo(id_tipo_empleado)

    # Crear respuesta detallada
    tipo_detallado = TipoEmpleadoDetallado(
        **tipo.__dict__,
        cantidad_empleados=cantidad_empleados
    )

    return tipo_detallado


@router.post(
    "/",
    response_model=TipoEmpleadoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear tipo de empleado",
    description="Crea un nuevo tipo de empleado en el sistema"
)
def crear_tipo_empleado(
        tipo_data: TipoEmpleadoCreate,
        db: Session = Depends(get_database)
):
    """
    Crea un nuevo tipo de empleado.

    - **nombre_tipo**: Nombre único del tipo (ej: ASALARIADO)
    - **descripcion**: Descripción opcional del tipo
    """
    repo = TipoEmpleadoRepository(db)

    # Validar que no exista
    if repo.exists_by_nombre(tipo_data.nombre_tipo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un tipo de empleado con nombre '{tipo_data.nombre_tipo}'"
        )

    # Crear tipo
    tipo = TipoEmpleado(**tipo_data.model_dump())
    tipo_creado = repo.create(tipo)

    return tipo_creado


@router.put(
    "/{id_tipo_empleado}",
    response_model=TipoEmpleadoResponse,
    summary="Actualizar tipo de empleado",
    description="Actualiza la información de un tipo de empleado existente"
)
def actualizar_tipo_empleado(
        id_tipo_empleado: int,
        tipo_update: TipoEmpleadoUpdate,
        db: Session = Depends(get_database)
):
    """
    Actualiza un tipo de empleado.

    - **id_tipo_empleado**: ID del tipo a actualizar
    - **nombre_tipo**: Nuevo nombre (opcional)
    - **descripcion**: Nueva descripción (opcional)
    """
    repo = TipoEmpleadoRepository(db)

    # Validar que exista
    tipo = repo.get_by_id(id_tipo_empleado)
    if not tipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipo de empleado con ID {id_tipo_empleado} no encontrado"
        )

    # Validar nombre único si se está cambiando
    if tipo_update.nombre_tipo and tipo_update.nombre_tipo != tipo.nombre_tipo:
        if repo.exists_by_nombre(tipo_update.nombre_tipo):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un tipo con nombre '{tipo_update.nombre_tipo}'"
            )

    # Actualizar
    update_data = tipo_update.model_dump(exclude_unset=True)
    tipo_actualizado = repo.update(tipo, update_data)

    return tipo_actualizado


@router.delete(
    "/{id_tipo_empleado}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar tipo de empleado",
    description="Elimina un tipo de empleado del sistema"
)
def eliminar_tipo_empleado(
        id_tipo_empleado: int,
        db: Session = Depends(get_database)
):
    """
    Elimina un tipo de empleado.

    - **id_tipo_empleado**: ID del tipo a eliminar

    **Nota**: No se puede eliminar si hay empleados asociados.
    """
    repo = TipoEmpleadoRepository(db)

    # Validar que exista
    tipo = repo.get_by_id(id_tipo_empleado)
    if not tipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipo de empleado con ID {id_tipo_empleado} no encontrado"
        )

    # Validar que no tenga empleados asociados
    from app.repositories.empleado_repository import EmpleadoRepository
    empleado_repo = EmpleadoRepository(db)
    cantidad_empleados = empleado_repo.count_by_tipo(id_tipo_empleado)

    if cantidad_empleados > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar: hay {cantidad_empleados} empleado(s) asociado(s)"
        )

    # Eliminar
    repo.delete(id_tipo_empleado)

    return None