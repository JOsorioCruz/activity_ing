"""
Endpoints para Empleados.
Operaciones CRUD completas para empleados.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app.api.dependencies import get_database
from app.services.empleado_service import EmpleadoService
from app.schemas.empleado import (
    EmpleadoCreate,
    EmpleadoUpdate,
    EmpleadoResponse,
    EmpleadoDetallado,
    EmpleadoListado
)
from app.utils.exceptions import EmpleadoNoEncontradoException, NominaException
from app.utils.helpers import calcular_anio_antiguedad

router = APIRouter()


@router.get(
    "/",
    response_model=List[EmpleadoListado],
    summary="Listar empleados",
    description="Obtiene lista de empleados con paginación y filtros"
)
def listar_empleados(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Límite de registros"),
    solo_activos: bool = Query(False, description="Solo mostrar empleados activos"),
    db: Session = Depends(get_database)
):
    """
    Lista empleados con opciones de paginación y filtro.
    
    - **skip**: Paginación - registros a saltar
    - **limit**: Paginación - máximo de registros
    - **solo_activos**: Filtrar solo empleados activos
    """
    service = EmpleadoService(db)
    empleados = service.listar_empleados(skip, limit, solo_activos)
    
    # Convertir a formato listado
    empleados_listado = []
    for emp in empleados:
        empleados_listado.append({
            "id_empleado": emp.id_empleado,
            "numero_identificacion": emp.numero_identificacion,
            "nombre_completo": emp.nombre_completo,
            "email": emp.email,
            "tipo_empleado_nombre": emp.tipo_empleado.nombre_tipo,
            "estado": emp.estado,
            "fecha_ingreso": emp.fecha_ingreso
        })
    
    return empleados_listado


@router.get(
    "/buscar",
    response_model=List[EmpleadoListado],
    summary="Buscar empleados",
    description="Busca empleados por nombre, apellido, identificación o email"
)
def buscar_empleados(
    q: str = Query(..., min_length=2, description="Término de búsqueda"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_database)
):
    """
    Busca empleados por término.
    
    - **q**: Término de búsqueda (mínimo 2 caracteres)
    """
    service = EmpleadoService(db)
    empleados = service.buscar_empleados(q, skip, limit)
    
    empleados_listado = []
    for emp in empleados:
        empleados_listado.append({
            "id_empleado": emp.id_empleado,
            "numero_identificacion": emp.numero_identificacion,
            "nombre_completo": emp.nombre_completo,
            "email": emp.email,
            "tipo_empleado_nombre": emp.tipo_empleado.nombre_tipo,
            "estado": emp.estado,
            "fecha_ingreso": emp.fecha_ingreso
        })
    
    return empleados_listado


@router.get(
    "/{id_empleado}",
    response_model=EmpleadoDetallado,
    summary="Obtener empleado",
    description="Obtiene información detallada de un empleado específico"
)
def obtener_empleado(
    id_empleado: int,
    db: Session = Depends(get_database)
):
    """
    Obtiene un empleado por ID con información detallada.
    
    - **id_empleado**: ID único del empleado
    """
    try:
        service = EmpleadoService(db)
        empleado = service.obtener_empleado(id_empleado)
        
        # Crear respuesta detallada
        empleado_detallado = {
            **empleado.__dict__,
            "tipo_empleado_nombre": empleado.tipo_empleado.nombre_tipo,
            "nombre_completo": empleado.nombre_completo,
            "anio_antiguedad": calcular_anio_antiguedad(empleado.fecha_ingreso)
        }
        
        return empleado_detallado
        
    except EmpleadoNoEncontradoException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.post(
    "/",
    response_model=EmpleadoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear empleado",
    description="Crea un nuevo empleado en el sistema"
)
def crear_empleado(
    empleado_data: EmpleadoCreate,
    db: Session = Depends(get_database)
):
    """
    Crea un nuevo empleado.
    
    Campos requeridos varían según el tipo de empleado:
    - **ASALARIADO**: salario_base
    - **POR_HORAS**: tarifa_hora
    - **POR_COMISION**: salario_base, porcentaje_comision
    - **TEMPORAL**: salario_base, fecha_fin_contrato
    """
    try:
        service = EmpleadoService(db)
        empleado = service.crear_empleado(empleado_data)
        return empleado
        
    except NominaException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear empleado: {str(e)}"
        )


@router.put(
    "/{id_empleado}",
    response_model=EmpleadoResponse,
    summary="Actualizar empleado",
    description="Actualiza la información de un empleado existente"
)
def actualizar_empleado(
    id_empleado: int,
    empleado_update: EmpleadoUpdate,
    db: Session = Depends(get_database)
):
    """
    Actualiza un empleado existente.
    
    - **id_empleado**: ID del empleado a actualizar
    - Todos los campos son opcionales
    """
    try:
        service = EmpleadoService(db)
        empleado = service.actualizar_empleado(id_empleado, empleado_update)
        return empleado
        
    except EmpleadoNoEncontradoException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except NominaException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


@router.delete(
    "/{id_empleado}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar empleado",
    description="Elimina un empleado del sistema"
)
def eliminar_empleado(
    id_empleado: int,
    db: Session = Depends(get_database)
):
    """
    Elimina un empleado.
    
    - **id_empleado**: ID del empleado a eliminar
    
    **Nota**: Esto eliminará también todas las nóminas asociadas.
    """
    try:
        service = EmpleadoService(db)
        service.eliminar_empleado(id_empleado)
        return None
        
    except EmpleadoNoEncontradoException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.get(
    "/antiguedad/{anio_minimos}",
    response_model=List[EmpleadoListado],
    summary="Empleados con antigüedad",
    description="Obtiene empleados con X anio de antigüedad mínimos"
)
def empleados_con_antiguedad(
    anio_minimos: int = Path(..., ge=0, description="anio mínimos de antigüedad"),
    db: Session = Depends(get_database)
):
    """
    Obtiene empleados con antigüedad mínima especificada.
    
    - **anio_minimos**: anio de antigüedad mínimos
    """
    service = EmpleadoService(db)
    empleados = service.obtener_empleados_con_antiguedad(anio_minimos)
    
    empleados_listado = []
    for emp in empleados:
        empleados_listado.append({
            "id_empleado": emp.id_empleado,
            "numero_identificacion": emp.numero_identificacion,
            "nombre_completo": emp.nombre_completo,
            "email": emp.email,
            "tipo_empleado_nombre": emp.tipo_empleado.nombre_tipo,
            "estado": emp.estado,
            "fecha_ingreso": emp.fecha_ingreso
        })
    
    return empleados_listado