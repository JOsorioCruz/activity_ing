"""
Módulo de modelos.
Exporta todos los modelos para fácil importación.
"""

from app.models.tipo_empleado import TipoEmpleado
from app.models.empleado import Empleado
from app.models.periodo_nomina import PeriodoNomina
from app.models.nomina import Nomina
from app.models.detalle_bono import DetalleBono
from app.models.detalle_beneficio import DetalleBeneficio
from app.models.detalle_deduccion import DetalleDeduccion
from app.models.auditoria_nomina import AuditoriaNomina

__all__ = [
    "TipoEmpleado",
    "Empleado",
    "PeriodoNomina",
    "Nomina",
    "DetalleBono",
    "DetalleBeneficio",
    "DetalleDeduccion",
    "AuditoriaNomina"
]