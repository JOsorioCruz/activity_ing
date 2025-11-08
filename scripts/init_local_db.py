"""
Script para inicializar la base de datos local con datos de prueba.
Ejecutar: python scripts/init_local_db.py
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date, timedelta
from app.db.session import engine, SessionLocal, reset_database
from app.db.base import Base
from app.models.tipo_empleado import TipoEmpleado
from app.models.empleado import Empleado
from app.models.periodo_nomina import PeriodoNomina
from app.utils.enums import TipoEmpleadoEnum, EstadoEmpleadoEnum, EstadoPeriodoEnum


def init_tipos_empleado(db: SessionLocal):
    """Inicializa los tipos de empleado."""
    print("\n[1/3] Creando tipos de empleado...")

    tipos = [
        TipoEmpleado(
            nombre_tipo=TipoEmpleadoEnum.ASALARIADO.value,
            descripcion="Empleado con salario fijo mensual. Elegible para bono de antigüedad (10% después de 5 años) y bono de alimentación ($1.000.000/mes)"
        ),
        TipoEmpleado(
            nombre_tipo=TipoEmpleadoEnum.POR_HORAS.value,
            descripcion="Empleado pagado por horas trabajadas. Horas extras (>40h) pagadas a 1.5x. Sin bonos. Elegible para fondo de ahorro después de 1 año"
        ),
        TipoEmpleado(
            nombre_tipo=TipoEmpleadoEnum.POR_COMISION.value,
            descripcion="Empleado con salario base más comisión sobre ventas. Bono adicional 3% si ventas >$20.000.000. Elegible para bono de alimentación"
        ),
        TipoEmpleado(
            nombre_tipo=TipoEmpleadoEnum.TEMPORAL.value,
            descripcion="Empleado con contrato de tiempo definido. Salario fijo mensual. Sin bonos ni beneficios adicionales"
        )
    ]

    for tipo in tipos:
        db.add(tipo)

    db.commit()
    print(f"    ✓ {len(tipos)} tipos de empleado creados")


def init_empleados(db: SessionLocal):
    """Inicializa empleados de ejemplo."""
    print("\n[2/3] Creando empleados de ejemplo...")

    # Obtener tipos de empleado
    tipo_asalariado = db.query(TipoEmpleado).filter_by(
        nombre_tipo=TipoEmpleadoEnum.ASALARIADO.value
    ).first()
    tipo_por_horas = db.query(TipoEmpleado).filter_by(
        nombre_tipo=TipoEmpleadoEnum.POR_HORAS.value
    ).first()
    tipo_por_comision = db.query(TipoEmpleado).filter_by(
        nombre_tipo=TipoEmpleadoEnum.POR_COMISION.value
    ).first()
    tipo_temporal = db.query(TipoEmpleado).filter_by(
        nombre_tipo=TipoEmpleadoEnum.TEMPORAL.value
    ).first()

    empleados = [
        # Empleado Asalariado con +5 años (recibe bono antigüedad)
        Empleado(
            numero_identificacion="1001234567",
            nombres="Carlos Alberto",
            apellidos="Rodríguez Pérez",
            email="carlos.rodriguez@empresa.com",
            telefono="3101234567",
            id_tipo_empleado=tipo_asalariado.id_tipo_empleado,
            fecha_ingreso=date(2018, 1, 15),
            estado=EstadoEmpleadoEnum.ACTIVO,
            salario_base=5000000.00
        ),

        # Empleado Asalariado con -5 años
        Empleado(
            numero_identificacion="1002345678",
            nombres="María Fernanda",
            apellidos="López García",
            email="maria.lopez@empresa.com",
            telefono="3109876543",
            id_tipo_empleado=tipo_asalariado.id_tipo_empleado,
            fecha_ingreso=date(2022, 6, 1),
            estado=EstadoEmpleadoEnum.ACTIVO,
            salario_base=4500000.00
        ),

        # Empleado Por Horas con +1 año (acepta fondo)
        Empleado(
            numero_identificacion="1003456789",
            nombres="Juan David",
            apellidos="Martínez Sánchez",
            email="juan.martinez@empresa.com",
            telefono="3207654321",
            id_tipo_empleado=tipo_por_horas.id_tipo_empleado,
            fecha_ingreso=date(2022, 3, 10),
            estado=EstadoEmpleadoEnum.ACTIVO,
            tarifa_hora=25000.00,
            acepta_fondo_ahorro=True
        ),

        # Empleado Por Horas con -1 año
        Empleado(
            numero_identificacion="1004567890",
            nombres="Ana María",
            apellidos="González Ruiz",
            email="ana.gonzalez@empresa.com",
            telefono="3156789012",
            id_tipo_empleado=tipo_por_horas.id_tipo_empleado,
            fecha_ingreso=date(2024, 8, 15),
            estado=EstadoEmpleadoEnum.ACTIVO,
            tarifa_hora=20000.00,
            acepta_fondo_ahorro=False
        ),

        # Empleado Por Comisión
        Empleado(
            numero_identificacion="1005678901",
            nombres="Luis Fernando",
            apellidos="Ramírez Castro",
            email="luis.ramirez@empresa.com",
            telefono="3118901234",
            id_tipo_empleado=tipo_por_comision.id_tipo_empleado,
            fecha_ingreso=date(2021, 9, 20),
            estado=EstadoEmpleadoEnum.ACTIVO,
            salario_base=2000000.00,
            porcentaje_comision=5.00
        ),

        # Empleado Temporal
        Empleado(
            numero_identificacion="1006789012",
            nombres="Sandra Patricia",
            apellidos="Vargas Mejía",
            email="sandra.vargas@empresa.com",
            telefono="3129012345",
            id_tipo_empleado=tipo_temporal.id_tipo_empleado,
            fecha_ingreso=date(2024, 10, 1),
            estado=EstadoEmpleadoEnum.ACTIVO,
            salario_base=2500000.00,
            fecha_fin_contrato=date(2025, 3, 31)
        )
    ]

    for empleado in empleados:
        db.add(empleado)

    db.commit()
    print(f"    ✓ {len(empleados)} empleados creados")


def init_periodos(db: SessionLocal):
    """Inicializa períodos de nómina."""
    print("\n[3/3] Creando períodos de nómina...")

    hoy = date.today()

    periodos = [
        # Período actual
        PeriodoNomina(
            anio=hoy.year,
            mes=hoy.month,
            fecha_inicio=date(hoy.year, hoy.month, 1),
            fecha_fin=date(hoy.year, hoy.month, 28) if hoy.month == 2 else date(hoy.year, hoy.month, 30),
            fecha_pago=date(hoy.year, hoy.month, 5) + timedelta(days=30),
            estado=EstadoPeriodoEnum.ABIERTO
        ),

        # Período siguiente
        PeriodoNomina(
            anio=hoy.year if hoy.month < 12 else hoy.year + 1,
            mes=hoy.month + 1 if hoy.month < 12 else 1,
            fecha_inicio=date(hoy.year if hoy.month < 12 else hoy.year + 1, hoy.month + 1 if hoy.month < 12 else 1, 1),
            fecha_fin=date(hoy.year if hoy.month < 12 else hoy.year + 1, hoy.month + 1 if hoy.month < 12 else 1, 28),
            fecha_pago=date(hoy.year if hoy.month < 12 else hoy.year + 1, hoy.month + 1 if hoy.month < 12 else 1, 5),
            estado=EstadoPeriodoEnum.ABIERTO
        )
    ]

    for periodo in periodos:
        db.add(periodo)

    db.commit()
    print(f"    ✓ {len(periodos)} períodos creados")


def main():
    """Función principal."""
    print("\n" + "=" * 60)
    print("INICIALIZACIÓN DE BASE DE DATOS LOCAL")
    print("=" * 60)

    # Reiniciar base de datos
    print("\n[PASO 1] Reiniciando base de datos...")
    reset_database()

    # Crear sesión
    db = SessionLocal()

    try:
        print("\n[PASO 2] Insertando datos de prueba...")

        # Insertar datos
        init_tipos_empleado(db)
        init_empleados(db)
        init_periodos(db)

        print("\n" + "=" * 60)
        print("✓ INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("\nPuedes iniciar el servidor con:")
        print("  python -m uvicorn app.main:app --reload")
        print("\nLuego visita: http://127.0.0.1:8000/docs\n")

    except Exception as e:
        print(f"\n[ERROR] Error al inicializar: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()