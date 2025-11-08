"""
Endpoints para Nómina.
Operaciones de cálculo y gestión de nóminas.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_database
from app.services.nomina_service import NominaService
from app.schemas.nomina import (
    NominaCreate,
    NominaUpdate,
    NominaResponse,
    NominaDetallada,
    NominaResumen,
    NominaCalculoRequest,
    NominaCalculoResponse
)
from app.utils.exceptions import (
    NominaException,
    EmpleadoNoEncontradoException,
    PeriodoNoEncontradoException,
    PeriodoCerradoException,
    SalarioNegativoException
)
from app.utils.helpers import calcular_anio_antiguedad

router = APIRouter()


@router.post(
    "/calcular",
    response_model=NominaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Calcular nómina",
    description="Calcula y crea una nómina para un empleado en un período"
)
def calcular_nomina(
        nomina_data: NominaCreate,
        usuario: str = Query("SYSTEM", description="Usuario que realiza el cálculo"),
        db: Session = Depends(get_database)
):
    """
    Calcula y crea una nueva nómina.

    El sistema calcula automáticamente:
    - Salario bruto según tipo de empleado
    - Bonos aplicables (antigüedad, ventas)
    - Beneficios (alimentación, fondo de ahorro)
    - Deducciones obligatorias (seg. social, ARL)
    - Salario neto final

    **Campos requeridos**:
    - **id_empleado**: ID del empleado
    - **id_periodo**: ID del período

    **Campos según tipo de empleado**:
    - **POR_HORAS**: horas_trabajadas, horas_extras
    - **POR_COMISION**: ventas_realizadas
    - **ASALARIADO**: ninguno adicional
    - **TEMPORAL**: ninguno adicional
    """
    try:
        service = NominaService(db)
        nomina = service.calcular_y_crear_nomina(nomina_data, usuario)
        return nomina

    except EmpleadoNoEncontradoException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except PeriodoNoEncontradoException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except PeriodoCerradoException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except SalarioNegativoException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except NominaException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular nómina: {str(e)}"
        )


@router.post(
    "/calcular-periodo",
    response_model=dict,
    summary="Calcular nóminas de período",
    description="Calcula nóminas para todos los empleados activos de un período"
)
def calcular_nominas_periodo(
        id_periodo: int = Query(..., description="ID del período"),
        usuario: str = Query("SYSTEM", description="Usuario que realiza el cálculo"),
        db: Session = Depends(get_database)
):
    """
    Calcula nóminas masivamente para un período.

    Procesa todos los empleados activos y calcula su nómina con valores por defecto:
    - Empleados asalariados: salario base
    - Empleados por horas: 0 horas (deben actualizarse después)
    - Empleados por comisión: $0 en ventas (deben actualizarse después)
    - Empleados temporales: salario base

    **Retorna**:
    - Total de empleados procesados
    - Nóminas exitosas
    - Nóminas fallidas con detalles de error
    """
    try:
        service = NominaService(db)
        resultado = service.calcular_nominas_periodo(id_periodo, usuario)
        return resultado

    except PeriodoNoEncontradoException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except PeriodoCerradoException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular nóminas: {str(e)}"
        )


@router.get(
    "/{id_nomina}",
    response_model=NominaDetallada,
    summary="Obtener nómina detallada",
    description="Obtiene una nómina con todos sus detalles"
)
def obtener_nomina(
        id_nomina: int,
        db: Session = Depends(get_database)
):
    """
    Obtiene una nómina por ID con información completa.

    Incluye:
    - Datos del empleado
    - Información del período
    - Detalles de bonos
    - Detalles de beneficios
    - Detalles de deducciones
    - Totales calculados
    """
    service = NominaService(db)
    nomina = service.obtener_nomina_detallada(id_nomina)

    if not nomina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nómina con ID {id_nomina} no encontrada"
        )

    # Construir respuesta detallada
    empleado_data = {
        "id_empleado": nomina.empleado.id_empleado,
        "numero_identificacion": nomina.empleado.numero_identificacion,
        "nombre_completo": nomina.empleado.nombre_completo,
        "email": nomina.empleado.email,
        "tipo_empleado_nombre": nomina.empleado.tipo_empleado.nombre_tipo,
        "estado": nomina.empleado.estado,
        "fecha_ingreso": nomina.empleado.fecha_ingreso
    }

    periodo_data = {
        "id_periodo": nomina.periodo.id_periodo,
        "anio": nomina.periodo.anio,
        "mes": nomina.periodo.mes,
        "fecha_inicio": nomina.periodo.fecha_inicio,
        "fecha_fin": nomina.periodo.fecha_fin,
        "fecha_pago": nomina.periodo.fecha_pago,
        "estado": nomina.periodo.estado,
        "fecha_creacion": nomina.periodo.fecha_creacion
    }

    nomina_detallada = {
        **nomina.__dict__,
        "empleado": empleado_data,
        "periodo": periodo_data,
        "bonos": [b.__dict__ for b in nomina.bonos],
        "beneficios": [b.__dict__ for b in nomina.beneficios],
        "deducciones": [d.__dict__ for d in nomina.deducciones],
        "total_ingresos": nomina.total_ingresos,
        "porcentaje_deducciones": nomina.porcentaje_deducciones
    }

    return nomina_detallada


@router.get(
    "/empleado/{id_empleado}",
    response_model=List[NominaResumen],
    summary="Nóminas de empleado",
    description="Obtiene todas las nóminas de un empleado"
)
def listar_nominas_empleado(
        id_empleado: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: Session = Depends(get_database)
):
    """
    Lista nóminas de un empleado específico.

    - **id_empleado**: ID del empleado
    - **skip**: Registros a saltar
    - **limit**: Límite de registros
    """
    service = NominaService(db)
    nominas = service.listar_nominas_empleado(id_empleado, skip, limit)

    nominas_resumen = []
    for nomina in nominas:
        nominas_resumen.append({
            "id_nomina": nomina.id_nomina,
            "empleado_nombre": nomina.empleado.nombre_completo,
            "empleado_identificacion": nomina.empleado.numero_identificacion,
            "periodo_texto": nomina.periodo.periodo_texto,
            "salario_bruto": nomina.salario_bruto,
            "salario_neto": nomina.salario_neto,
            "fecha_calculo": nomina.fecha_calculo
        })

    return nominas_resumen


@router.get(
    "/periodo/{id_periodo}",
    response_model=List[NominaResumen],
    summary="Nóminas de período",
    description="Obtiene todas las nóminas de un período"
)
def listar_nominas_periodo(
        id_periodo: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: Session = Depends(get_database)
):
    """
    Lista nóminas de un período específico.

    - **id_periodo**: ID del período
    - **skip**: Registros a saltar
    - **limit**: Límite de registros
    """
    service = NominaService(db)
    nominas = service.listar_nominas_periodo(id_periodo, skip, limit)

    nominas_resumen = []
    for nomina in nominas:
        nominas_resumen.append({
            "id_nomina": nomina.id_nomina,
            "empleado_nombre": nomina.empleado.nombre_completo,
            "empleado_identificacion": nomina.empleado.numero_identificacion,
            "periodo_texto": nomina.periodo.periodo_texto,
            "salario_bruto": nomina.salario_bruto,
            "salario_neto": nomina.salario_neto,
            "fecha_calculo": nomina.fecha_calculo
        })

    return nominas_resumen


@router.get(
    "/periodo/{id_periodo}/resumen",
    response_model=dict,
    summary="Resumen de período",
    description="Obtiene estadísticas resumidas de un período"
)
def resumen_periodo(
        id_periodo: int,
        db: Session = Depends(get_database)
):
    """
    Obtiene resumen estadístico de un período.

    Incluye:
    - Total de nóminas
    - Total de salario bruto
    - Total de salario neto
    - Total de bonos
    - Total de beneficios
    - Total de deducciones
    - Promedio de salario neto
    """
    try:
        service = NominaService(db)
        resumen = service.obtener_resumen_periodo(id_periodo)
        return resumen

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener resumen: {str(e)}"
        )


@router.put(
    "/{id_nomina}",
    response_model=NominaResponse,
    summary="Recalcular nómina",
    description="Recalcula una nómina con nuevos datos de entrada"
)
def recalcular_nomina(
        id_nomina: int,
        nomina_update: NominaUpdate,
        usuario: str = Query("SYSTEM", description="Usuario que recalcula"),
        db: Session = Depends(get_database)
):
    """
    Recalcula una nómina existente.

    Útil para actualizar:
    - Horas trabajadas y extras (empleados por horas)
    - Ventas realizadas (empleados por comisión)

    El sistema recalcula automáticamente todos los valores.

    **Nota**: Solo se puede recalcular si el período está abierto.
    """
    try:
        service = NominaService(db)
        nomina = service.recalcular_nomina(id_nomina, nomina_update, usuario)
        return nomina

    except NominaException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except PeriodoCerradoException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except SalarioNegativoException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al recalcular nómina: {str(e)}"
        )


@router.delete(
    "/{id_nomina}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar nómina",
    description="Elimina una nómina"
)
def eliminar_nomina(
        id_nomina: int,
        usuario: str = Query("SYSTEM", description="Usuario que elimina"),
        db: Session = Depends(get_database)
):
    """
    Elimina una nómina.

    - **id_nomina**: ID de la nómina a eliminar

    **Nota**: Solo se puede eliminar si el período está abierto.
    """
    try:
        service = NominaService(db)
        eliminado = service.eliminar_nomina(id_nomina, usuario)

        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nómina con ID {id_nomina} no encontrada"
            )

        return None

    except PeriodoCerradoException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar nómina: {str(e)}"
        )