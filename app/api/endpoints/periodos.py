"""
Endpoints para Períodos de Nómina.
Gestión de períodos mensuales.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app.api.dependencies import get_database
from app.repositories.periodo_repository import PeriodoNominaRepository
from app.models.periodo_nomina import PeriodoNomina
from app.schemas.periodo_nomina import (
    PeriodoNominaCreate,
    PeriodoNominaUpdate,
    PeriodoNominaResponse,
    PeriodoNominaDetallado
)
from app.utils.exceptions import NominaException, PeriodoNoEncontradoException

router = APIRouter()


@router.get(
    "/",
    response_model=List[PeriodoNominaResponse],
    summary="Listar períodos",
    description="Obtiene todos los períodos de nómina"
)
def listar_periodos(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: Session = Depends(get_database)
):
    """
    Lista períodos de nómina.

    - **skip**: Registros a saltar
    - **limit**: Límite de registros
    """
    repo = PeriodoNominaRepository(db)
    periodos = repo.get_all(skip=skip, limit=limit, order_by="anio", order_desc=True)
    return periodos


@router.get(
    "/ultimos",
    response_model=List[PeriodoNominaResponse],
    summary="Últimos períodos",
    description="Obtiene los últimos N períodos"
)
def ultimos_periodos(
        cantidad: int = Query(12, ge=1, le=24, description="Cantidad de períodos"),
        db: Session = Depends(get_database)
):
    """
    Obtiene los últimos períodos ordenados por fecha.

    - **cantidad**: Cantidad de períodos a retornar (máximo 24)
    """
    repo = PeriodoNominaRepository(db)
    periodos = repo.get_ultimos(cantidad)
    return periodos


@router.get(
    "/abiertos",
    response_model=List[PeriodoNominaResponse],
    summary="Períodos abiertos",
    description="Obtiene períodos en estado ABIERTO"
)
def periodos_abiertos(
        db: Session = Depends(get_database)
):
    """Obtiene todos los períodos abiertos."""
    repo = PeriodoNominaRepository(db)
    periodos = repo.get_abiertos()
    return periodos


@router.get(
    "/{id_periodo}",
    response_model=PeriodoNominaDetallado,
    summary="Obtener período",
    description="Obtiene información detallada de un período"
)
def obtener_periodo(
        id_periodo: int,
        db: Session = Depends(get_database)
):
    """
    Obtiene un período por ID con estadísticas.

    - **id_periodo**: ID único del período
    """
    repo = PeriodoNominaRepository(db)
    periodo = repo.get_by_id(id_periodo)

    if not periodo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Período con ID {id_periodo} no encontrado"
        )

    # Obtener estadísticas
    from app.repositories.nomina_repository import NominaRepository
    nomina_repo = NominaRepository(db)
    nominas = nomina_repo.get_by_periodo(id_periodo)

    cantidad_nominas = len(nominas)
    total_nomina = sum(float(n.salario_neto) for n in nominas)

    periodo_detallado = PeriodoNominaDetallado(
        **periodo.__dict__,
        cantidad_nominas=cantidad_nominas,
        total_nomina=total_nomina,
        periodo_texto=periodo.periodo_texto
    )

    return periodo_detallado


@router.get(
    "/buscar/{anio}/{mes}",
    response_model=PeriodoNominaResponse,
    summary="Buscar per\u00edodo por a\u00f1o/mes",
    description="Obtiene un per\u00edodo espec\u00edfico por a\u00f1o y mes"
)
def buscar_periodo_por_fecha(
        anio: int = Path(..., ge=2000, le=2100, description="A\u00f1o del per\u00edodo"),
        mes: int = Path(..., ge=1, le=12, description="Mes del per\u00edodo"),
        db: Session = Depends(get_database)
):
    """
    Busca período por año y mes.

    - **anio**: Año (ej: 2024)
    - **mes**: Mes (1-12)
    """
    repo = PeriodoNominaRepository(db)
    periodo = repo.get_by_anio_mes(anio, mes)

    if not periodo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe período para {anio}-{mes:02d}"
        )

    return periodo


@router.post(
    "/",
    response_model=PeriodoNominaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear período",
    description="Crea un nuevo período de nómina"
)
def crear_periodo(
        periodo_data: PeriodoNominaCreate,
        db: Session = Depends(get_database)
):
    """
    Crea un nuevo período de nómina.

    - **anio**: Año del período
    - **mes**: Mes del período (1-12)
    - **fecha_inicio**: Fecha de inicio
    - **fecha_fin**: Fecha de fin
    - **fecha_pago**: Fecha programada de pago
    """
    repo = PeriodoNominaRepository(db)

    # Validar que no exista
    if repo.exists_periodo(periodo_data.anio, periodo_data.mes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un período para {periodo_data.anio}-{periodo_data.mes:02d}"
        )

    # Crear período
    periodo = PeriodoNomina(**periodo_data.model_dump())
    periodo_creado = repo.create(periodo)

    return periodo_creado


@router.put(
    "/{id_periodo}",
    response_model=PeriodoNominaResponse,
    summary="Actualizar período",
    description="Actualiza información de un período"
)
def actualizar_periodo(
        id_periodo: int,
        periodo_update: PeriodoNominaUpdate,
        db: Session = Depends(get_database)
):
    """
    Actualiza un período existente.

    - **id_periodo**: ID del período
    - **fecha_pago**: Nueva fecha de pago (opcional)
    - **estado**: Nuevo estado (opcional)
    """
    repo = PeriodoNominaRepository(db)

    periodo = repo.get_by_id(id_periodo)
    if not periodo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Período con ID {id_periodo} no encontrado"
        )

    update_data = periodo_update.model_dump(exclude_unset=True)
    periodo_actualizado = repo.update(periodo, update_data)

    return periodo_actualizado


@router.delete(
    "/{id_periodo}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar período",
    description="Elimina un período de nómina"
)
def eliminar_periodo(
        id_periodo: int,
        db: Session = Depends(get_database)
):
    """
    Elimina un período.

    - **id_periodo**: ID del período a eliminar

    **Nota**: No se puede eliminar si tiene nóminas asociadas.
    """
    repo = PeriodoNominaRepository(db)

    periodo = repo.get_by_id(id_periodo)
    if not periodo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Período con ID {id_periodo} no encontrado"
        )

    # Validar que no tenga nóminas
    from app.repositories.nomina_repository import NominaRepository
    nomina_repo = NominaRepository(db)
    cantidad_nominas = nomina_repo.count_by_periodo(id_periodo)

    if cantidad_nominas > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar: hay {cantidad_nominas} nómina(s) asociada(s)"
        )

    repo.delete(id_periodo)
    return None