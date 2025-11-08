"""
Módulo de schemas Pydantic.
Exporta todos los schemas para fácil importación.
"""

from app.schemas.tipo_empleado import (
    TipoEmpleadoBase,
    TipoEmpleadoCreate,
    TipoEmpleadoUpdate,
    TipoEmpleadoResponse,
    TipoEmpleadoDetallado
)

from app.schemas.empleado import (
    EmpleadoBase,
    EmpleadoCreate,
    EmpleadoUpdate,
    EmpleadoResponse,
    EmpleadoDetallado,
    EmpleadoListado
)

from app.schemas.periodo_nomina import (
    PeriodoNominaBase,
    PeriodoNominaCreate,
    PeriodoNominaUpdate,
    PeriodoNominaResponse,
    PeriodoNominaDetallado
)

from app.schemas.nomina import (
    NominaBase,
    NominaCreate,
    NominaUpdate,
    NominaResponse,
    NominaDetallada,
    NominaResumen,
    NominaCalculoRequest,
    NominaCalculoResponse,
    DetalleBonoResponse,
    DetalleBeneficioResponse,
    DetalleDeduccionResponse
)

__all__ = [
    # Tipo Empleado
    "TipoEmpleadoBase",
    "TipoEmpleadoCreate",
    "TipoEmpleadoUpdate",
    "TipoEmpleadoResponse",
    "TipoEmpleadoDetallado",

    # Empleado
    "EmpleadoBase",
    "EmpleadoCreate",
    "EmpleadoUpdate",
    "EmpleadoResponse",
    "EmpleadoDetallado",
    "EmpleadoListado",

    # Período
    "PeriodoNominaBase",
    "PeriodoNominaCreate",
    "PeriodoNominaUpdate",
    "PeriodoNominaResponse",
    "PeriodoNominaDetallado",

    # Nómina
    "NominaBase",
    "NominaCreate",
    "NominaUpdate",
    "NominaResponse",
    "NominaDetallada",
    "NominaResumen",
    "NominaCalculoRequest",
    "NominaCalculoResponse",
    "DetalleBonoResponse",
    "DetalleBeneficioResponse",
    "DetalleDeduccionResponse"
]