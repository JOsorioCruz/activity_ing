# Modelado de Base de Datos - Sistema de Nómina

## Análisis del Dominio

El sistema de nómina requiere gestionar diferentes tipos de empleados con reglas específicas de cálculo salarial, beneficios y deducciones. El modelo debe ser flexible para soportar los cuatro tipos de empleados y sus características particulares.

## Modelo Entidad-Relación

### Entidades Principales:
1. **Empleado** - Información base de todos los empleados
2. **TipoEmpleado** - Catálogo de tipos de empleado
3. **Nomina** - Registro mensual de cálculos de nómina
4. **Deduccion** - Deducciones aplicadas en cada nómina
5. **Beneficio** - Beneficios otorgados en cada nómina

---

## DDL (Data Definition Language)

### 1. Tabla: tipo_empleado
Catálogo con los tipos de empleado del sistema.

```sql
-- Tabla de catálogo para tipos de empleado
CREATE TABLE tipo_empleado (
    id_tipo_empleado INT PRIMARY KEY AUTO_INCREMENT,
    nombre_tipo VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    COMMENT 'Catálogo de tipos de empleado: Asalariado, Por Horas, Por Comisión, Temporal'
);

-- Índice para búsquedas por nombre
CREATE INDEX idx_tipo_nombre ON tipo_empleado(nombre_tipo);
```

**Explicación:**
- `id_tipo_empleado`: Identificador único del tipo
- `nombre_tipo`: Nombre descriptivo (Asalariado, Por Horas, etc.)
- `descripcion`: Detalles adicionales sobre el tipo
- Se usa UNIQUE en nombre_tipo para evitar duplicados

---

### 2. Tabla: empleado
Almacena la información personal y laboral de cada empleado.

```sql
-- Tabla principal de empleados
CREATE TABLE empleado (
    id_empleado INT PRIMARY KEY AUTO_INCREMENT,
    numero_identificacion VARCHAR(20) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    telefono VARCHAR(20),
    
    -- Relación con tipo de empleado
    id_tipo_empleado INT NOT NULL,
    
    -- Información laboral
    fecha_ingreso DATE NOT NULL,
    fecha_salida DATE DEFAULT NULL,
    estado ENUM('ACTIVO', 'INACTIVO', 'SUSPENDIDO') DEFAULT 'ACTIVO',
    
    -- Información salarial base (varía según tipo)
    salario_base DECIMAL(12, 2) DEFAULT 0.00,
    tarifa_hora DECIMAL(10, 2) DEFAULT 0.00,
    porcentaje_comision DECIMAL(5, 2) DEFAULT 0.00,
    
    -- Información adicional
    acepta_fondo_ahorro BOOLEAN DEFAULT FALSE,
    fecha_fin_contrato DATE DEFAULT NULL, -- Solo para temporales
    
    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Llaves foráneas
    FOREIGN KEY (id_tipo_empleado) REFERENCES tipo_empleado(id_tipo_empleado),
    
    -- Constraints de validación
    CONSTRAINT chk_salario_base CHECK (salario_base >= 0),
    CONSTRAINT chk_tarifa_hora CHECK (tarifa_hora >= 0),
    CONSTRAINT chk_porcentaje_comision CHECK (porcentaje_comision >= 0 AND porcentaje_comision <= 100),
    
    COMMENT 'Tabla principal que almacena información de todos los empleados'
);

-- Índices para optimizar consultas
CREATE INDEX idx_empleado_tipo ON empleado(id_tipo_empleado);
CREATE INDEX idx_empleado_estado ON empleado(estado);
CREATE INDEX idx_empleado_fecha_ingreso ON empleado(fecha_ingreso);
CREATE INDEX idx_empleado_nombre_completo ON empleado(nombres, apellidos);
```

**Explicación:**
- `numero_identificacion`: Cédula o documento único
- `id_tipo_empleado`: Relaciona con el tipo de empleado
- `salario_base`: Usado por Asalariados, Por Comisión y Temporales
- `tarifa_hora`: Usado solo por Empleados Por Horas
- `porcentaje_comision`: Usado solo por Empleados Por Comisión
- `acepta_fondo_ahorro`: Flag para Empleados Por Horas con +1 año
- `fecha_fin_contrato`: Específico para Empleados Temporales
- `estado`: Permite gestionar empleados activos/inactivos

---

### 3. Tabla: periodo_nomina
Define los períodos de cálculo de nómina.

```sql
-- Tabla para gestionar períodos de nómina
CREATE TABLE periodo_nomina (
    id_periodo INT PRIMARY KEY AUTO_INCREMENT,
    año INT NOT NULL,
    mes INT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    fecha_pago DATE NOT NULL,
    estado ENUM('ABIERTO', 'EN_PROCESO', 'CERRADO', 'PAGADO') DEFAULT 'ABIERTO',
    
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint para validar mes
    CONSTRAINT chk_mes CHECK (mes BETWEEN 1 AND 12),
    
    -- Constraint para asegurar unicidad de período
    UNIQUE KEY uk_periodo (año, mes),
    
    COMMENT 'Períodos mensuales para cálculo de nómina'
);

-- Índice para búsquedas por fecha
CREATE INDEX idx_periodo_fecha ON periodo_nomina(año, mes);
CREATE INDEX idx_periodo_estado ON periodo_nomina(estado);
```

**Explicación:**
- Gestiona los períodos mensuales de nómina
- `estado`: Controla el flujo del proceso de nómina
- La combinación año-mes es única para evitar duplicados

---

### 4. Tabla: nomina
Registra el cálculo de nómina para cada empleado en cada período.

```sql
-- Tabla principal de cálculos de nómina
CREATE TABLE nomina (
    id_nomina INT PRIMARY KEY AUTO_INCREMENT,
    id_empleado INT NOT NULL,
    id_periodo INT NOT NULL,
    
    -- Datos específicos del período
    horas_trabajadas DECIMAL(6, 2) DEFAULT 0.00,
    horas_extras DECIMAL(6, 2) DEFAULT 0.00,
    ventas_realizadas DECIMAL(15, 2) DEFAULT 0.00,
    
    -- Cálculos de salario
    salario_bruto DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    total_bonos DECIMAL(12, 2) DEFAULT 0.00,
    total_beneficios DECIMAL(12, 2) DEFAULT 0.00,
    total_deducciones DECIMAL(12, 2) DEFAULT 0.00,
    salario_neto DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    
    -- Auditoría
    fecha_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    calculado_por VARCHAR(100),
    
    -- Llaves foráneas
    FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado),
    FOREIGN KEY (id_periodo) REFERENCES periodo_nomina(id_periodo),
    
    -- Un empleado solo puede tener una nómina por período
    UNIQUE KEY uk_nomina_empleado_periodo (id_empleado, id_periodo),
    
    -- Validaciones
    CONSTRAINT chk_horas_trabajadas CHECK (horas_trabajadas >= 0),
    CONSTRAINT chk_horas_extras CHECK (horas_extras >= 0),
    CONSTRAINT chk_ventas CHECK (ventas_realizadas >= 0),
    CONSTRAINT chk_salario_neto CHECK (salario_neto >= 0),
    
    COMMENT 'Registro de cálculo de nómina por empleado y período'
);

-- Índices para optimizar consultas
CREATE INDEX idx_nomina_empleado ON nomina(id_empleado);
CREATE INDEX idx_nomina_periodo ON nomina(id_periodo);
CREATE INDEX idx_nomina_fecha ON nomina(fecha_calculo);
```

**Explicación:**
- `horas_trabajadas` y `horas_extras`: Solo para Empleados Por Horas
- `ventas_realizadas`: Solo para Empleados Por Comisión
- `salario_bruto`: Salario antes de deducciones y beneficios
- `salario_neto`: Resultado final después de todos los cálculos
- Constraint `chk_salario_neto` garantiza que nunca sea negativo (regla de negocio)

---

### 5. Tabla: detalle_bono
Registra los bonos aplicados a cada nómina.

```sql
-- Tabla para detallar bonos otorgados
CREATE TABLE detalle_bono (
    id_detalle_bono INT PRIMARY KEY AUTO_INCREMENT,
    id_nomina INT NOT NULL,
    tipo_bono VARCHAR(100) NOT NULL,
    descripcion TEXT,
    monto DECIMAL(12, 2) NOT NULL,
    porcentaje_aplicado DECIMAL(5, 2),
    
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_nomina) REFERENCES nomina(id_nomina) ON DELETE CASCADE,
    
    CONSTRAINT chk_monto_bono CHECK (monto >= 0),
    
    COMMENT 'Detalle de bonos aplicados: Antigüedad, Ventas, etc.'
);

CREATE INDEX idx_bono_nomina ON detalle_bono(id_nomina);
CREATE INDEX idx_bono_tipo ON detalle_bono(tipo_bono);
```

**Explicación:**
- `tipo_bono`: Identifica el tipo (ej: "Bono Antigüedad", "Bono Ventas")
- `porcentaje_aplicado`: Guarda el % usado para el cálculo
- ON DELETE CASCADE: Si se elimina una nómina, se eliminan sus bonos

---

### 6. Tabla: detalle_beneficio
Registra los beneficios aplicados a cada nómina.

```sql
-- Tabla para detallar beneficios otorgados
CREATE TABLE detalle_beneficio (
    id_detalle_beneficio INT PRIMARY KEY AUTO_INCREMENT,
    id_nomina INT NOT NULL,
    tipo_beneficio VARCHAR(100) NOT NULL,
    descripcion TEXT,
    monto DECIMAL(12, 2) NOT NULL,
    
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_nomina) REFERENCES nomina(id_nomina) ON DELETE CASCADE,
    
    CONSTRAINT chk_monto_beneficio CHECK (monto >= 0),
    
    COMMENT 'Detalle de beneficios: Bono Alimentación, Fondo de Ahorro, etc.'
);

CREATE INDEX idx_beneficio_nomina ON detalle_beneficio(id_nomina);
CREATE INDEX idx_beneficio_tipo ON detalle_beneficio(tipo_beneficio);
```

**Explicación:**
- Similar a bonos pero para beneficios
- Ejemplos: "Bono Alimentación", "Aporte Fondo de Ahorro"

---

### 7. Tabla: detalle_deduccion
Registra las deducciones aplicadas a cada nómina.

```sql
-- Tabla para detallar deducciones aplicadas
CREATE TABLE detalle_deduccion (
    id_detalle_deduccion INT PRIMARY KEY AUTO_INCREMENT,
    id_nomina INT NOT NULL,
    tipo_deduccion VARCHAR(100) NOT NULL,
    descripcion TEXT,
    monto DECIMAL(12, 2) NOT NULL,
    porcentaje_aplicado DECIMAL(5, 2),
    base_calculo DECIMAL(12, 2),
    
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_nomina) REFERENCES nomina(id_nomina) ON DELETE CASCADE,
    
    CONSTRAINT chk_monto_deduccion CHECK (monto >= 0),
    
    COMMENT 'Detalle de deducciones: Seguridad Social, Pensión, ARL, Fondo Ahorro'
);

CREATE INDEX idx_deduccion_nomina ON detalle_deduccion(id_nomina);
CREATE INDEX idx_deduccion_tipo ON detalle_deduccion(tipo_deduccion);
```

**Explicación:**
- `tipo_deduccion`: "Seguridad Social", "Pensión", "ARL", etc.
- `base_calculo`: Monto sobre el cual se calculó la deducción
- `porcentaje_aplicado`: % usado (ej: 4% para Seguridad Social)

---

### 8. Tabla: auditoria_nomina
Registra cambios y cálculos en las nóminas.

```sql
-- Tabla de auditoría para trazabilidad
CREATE TABLE auditoria_nomina (
    id_auditoria INT PRIMARY KEY AUTO_INCREMENT,
    id_nomina INT NOT NULL,
    accion VARCHAR(50) NOT NULL,
    usuario VARCHAR(100),
    descripcion TEXT,
    valores_anteriores JSON,
    valores_nuevos JSON,
    
    fecha_accion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_nomina) REFERENCES nomina(id_nomina),
    
    COMMENT 'Auditoría de cambios en nómina para trazabilidad'
);

CREATE INDEX idx_auditoria_nomina ON auditoria_nomina(id_nomina);
CREATE INDEX idx_auditoria_fecha ON auditoria_nomina(fecha_accion);
CREATE INDEX idx_auditoria_accion ON auditoria_nomina(accion);
```

**Explicación:**
- Mantiene historial de cambios
- `valores_anteriores` y `valores_nuevos`: JSON para flexibilidad
- Útil para cumplimiento normativo y debugging

---

## DML (Data Manipulation Language)

### Inserción de Datos Iniciales

#### 1. Tipos de Empleado

```sql
-- Insertar catálogo de tipos de empleado
INSERT INTO tipo_empleado (nombre_tipo, descripcion) VALUES
('ASALARIADO', 'Empleado con salario fijo mensual. Elegible para bono de antigüedad (10% después de 5 años) y bono de alimentación ($1.000.000/mes)'),
('POR_HORAS', 'Empleado pagado por horas trabajadas. Horas extras (>40h) pagadas a 1.5x. Sin bonos. Elegible para fondo de ahorro después de 1 año'),
('POR_COMISION', 'Empleado con salario base más comisión sobre ventas. Bono adicional 3% si ventas >$20.000.000. Elegible para bono de alimentación'),
('TEMPORAL', 'Empleado con contrato de tiempo definido. Salario fijo mensual. Sin bonos ni beneficios adicionales');

-- Verificar inserción
SELECT * FROM tipo_empleado;
```

**Explicación:**
- Se crean los 4 tipos de empleado según especificaciones
- La descripción incluye las reglas principales de cada tipo

---

#### 2. Empleados de Ejemplo

```sql
-- Empleado Asalariado con más de 5 años (recibe bono de antigüedad)
INSERT INTO empleado (
    numero_identificacion, nombres, apellidos, email, telefono,
    id_tipo_empleado, fecha_ingreso, estado, salario_base
) VALUES (
    '1001234567', 'Carlos Alberto', 'Rodríguez Pérez', 
    'carlos.rodriguez@empresa.com', '3101234567',
    1, -- ASALARIADO
    '2018-01-15', -- Más de 5 años
    'ACTIVO',
    5000000.00
);

-- Empleado Asalariado con menos de 5 años (NO recibe bono de antigüedad)
INSERT INTO empleado (
    numero_identificacion, nombres, apellidos, email, telefono,
    id_tipo_empleado, fecha_ingreso, estado, salario_base
) VALUES (
    '1002345678', 'María Fernanda', 'López García',
    'maria.lopez@empresa.com', '3109876543',
    1, -- ASALARIADO
    '2022-06-01', -- Menos de 5 años
    'ACTIVO',
    4500000.00
);

-- Empleado Por Horas con más de 1 año (acepta fondo de ahorro)
INSERT INTO empleado (
    numero_identificacion, nombres, apellidos, email, telefono,
    id_tipo_empleado, fecha_ingreso, estado, tarifa_hora, acepta_fondo_ahorro
) VALUES (
    '1003456789', 'Juan David', 'Martínez Sánchez',
    'juan.martinez@empresa.com', '3207654321',
    2, -- POR_HORAS
    '2022-03-10', -- Más de 1 año
    'ACTIVO',
    25000.00, -- Tarifa por hora
    TRUE -- Acepta fondo de ahorro
);

-- Empleado Por Horas con menos de 1 año
INSERT INTO empleado (
    numero_identificacion, nombres, apellidos, email, telefono,
    id_tipo_empleado, fecha_ingreso, estado, tarifa_hora, acepta_fondo_ahorro
) VALUES (
    '1004567890', 'Ana María', 'González Ruiz',
    'ana.gonzalez@empresa.com', '3156789012',
    2, -- POR_HORAS
    '2024-08-15', -- Menos de 1 año
    'ACTIVO',
    20000.00,
    FALSE
);

-- Empleado Por Comisión con ventas altas
INSERT INTO empleado (
    numero_identificacion, nombres, apellidos, email, telefono,
    id_tipo_empleado, fecha_ingreso, estado, salario_base, porcentaje_comision
) VALUES (
    '1005678901', 'Luis Fernando', 'Ramírez Castro',
    'luis.ramirez@empresa.com', '3118901234',
    3, -- POR_COMISION
    '2021-09-20',
    'ACTIVO',
    2000000.00, -- Salario base
    5.00 -- 5% de comisión
);

-- Empleado Temporal
INSERT INTO empleado (
    numero_identificacion, nombres, apellidos, email, telefono,
    id_tipo_empleado, fecha_ingreso, estado, salario_base, fecha_fin_contrato
) VALUES (
    '1006789012', 'Sandra Patricia', 'Vargas Mejía',
    'sandra.vargas@empresa.com', '3129012345',
    4, -- TEMPORAL
    '2024-10-01',
    'ACTIVO',
    2500000.00,
    '2025-03-31' -- Contrato por 6 meses
);

-- Verificar inserción de empleados
SELECT 
    e.numero_identificacion,
    CONCAT(e.nombres, ' ', e.apellidos) AS nombre_completo,
    te.nombre_tipo AS tipo_empleado,
    e.fecha_ingreso,
    e.estado,
    e.salario_base,
    e.tarifa_hora,
    e.porcentaje_comision
FROM empleado e
INNER JOIN tipo_empleado te ON e.id_tipo_empleado = te.id_tipo_empleado;
```

**Explicación:**
- Se crean ejemplos de cada tipo de empleado
- Los empleados reflejan diferentes escenarios (antigüedad, aceptación de fondos, etc.)
- Los datos son realistas para Colombia (salarios, formatos de identificación)

---

#### 3. Período de Nómina

```sql
-- Crear período de nómina para Noviembre 2024
INSERT INTO periodo_nomina (año, mes, fecha_inicio, fecha_fin, fecha_pago, estado)
VALUES (
    2024,
    11,
    '2024-11-01',
    '2024-11-30',
    '2024-12-05',
    'ABIERTO'
);

-- Crear período de nómina para Diciembre 2024
INSERT INTO periodo_nomina (año, mes, fecha_inicio, fecha_fin, fecha_pago, estado)
VALUES (
    2024,
    12,
    '2024-12-01',
    '2024-12-31',
    '2025-01-05',
    'ABIERTO'
);

-- Verificar períodos creados
SELECT 
    id_periodo,
    CONCAT(año, '-', LPAD(mes, 2, '0')) AS periodo,
    fecha_inicio,
    fecha_fin,
    fecha_pago,
    estado
FROM periodo_nomina
ORDER BY año DESC, mes DESC;
```

---

#### 4. Ejemplo de Nómina Completa

```sql
-- Ejemplo: Nómina para Carlos Alberto (Asalariado con +5 años)
-- Salario: $5.000.000
-- Bono antigüedad (10%): $500.000
-- Bono alimentación: $1.000.000
-- Deducción Seg.Social+Pensión (4%): $200.000
-- Deducción ARL (0.522%): $26.100

-- 1. Insertar registro de nómina
INSERT INTO nomina (
    id_empleado,
    id_periodo,
    salario_bruto,
    total_bonos,
    total_beneficios,
    total_deducciones,
    salario_neto,
    calculado_por
) VALUES (
    1, -- Carlos Alberto
    1, -- Noviembre 2024
    5000000.00, -- Salario bruto
    500000.00, -- Bono antigüedad
    1000000.00, -- Bono alimentación
    226100.00, -- Total deducciones
    6273900.00, -- Salario neto
    'SYSTEM'
);

-- 2. Registrar bonos
INSERT INTO detalle_bono (id_nomina, tipo_bono, descripcion, monto, porcentaje_aplicado)
VALUES (
    1,
    'BONO_ANTIGUEDAD',
    'Bono por antigüedad mayor a 5 años',
    500000.00,
    10.00
);

-- 3. Registrar beneficios
INSERT INTO detalle_beneficio (id_nomina, tipo_beneficio, descripcion, monto)
VALUES (
    1,
    'BONO_ALIMENTACION',
    'Subsidio de alimentación mensual',
    1000000.00
);

-- 4. Registrar deducciones
INSERT INTO detalle_deduccion (
    id_nomina, tipo_deduccion, descripcion, monto, porcentaje_aplicado, base_calculo
) VALUES
(
    1,
    'SEGURIDAD_SOCIAL_PENSION',
    'Aporte a Seguridad Social y Pensión',
    200000.00,
    4.00,
    5000000.00
),
(
    1,
    'ARL',
    'Aporte a Riesgos Laborales',
    26100.00,
    0.522,
    5000000.00
);
```

**Explicación del Cálculo:**
- **Salario Bruto**: $5.000.000
- **Bonos**: $500.000 (10% por antigüedad)
- **Beneficios**: $1.000.000 (alimentación)
- **Deducciones**: 
  - Seg. Social + Pensión: $200.000 (4% de $5.000.000)
  - ARL: $26.100 (0.522% de $5.000.000)
- **Salario Neto**: $5.000.000 + $500.000 + $1.000.000 - $226.100 = **$6.273.900**

---

### Consultas Útiles

#### Consulta 1: Resumen de Nómina por Empleado

```sql
-- Obtener resumen completo de nómina
SELECT 
    e.numero_identificacion,
    CONCAT(e.nombres, ' ', e.apellidos) AS nombre_completo,
    te.nombre_tipo AS tipo_empleado,
    CONCAT(pn.año, '-', LPAD(pn.mes, 2, '0')) AS periodo,
    n.salario_bruto,
    n.total_bonos,
    n.total_beneficios,
    n.total_deducciones,
    n.salario_neto,
    pn.fecha_pago
FROM nomina n
INNER JOIN empleado e ON n.id_empleado = e.id_empleado
INNER JOIN tipo_empleado te ON e.id_tipo_empleado = te.id_tipo_empleado
INNER JOIN periodo_nomina pn ON n.id_periodo = pn.id_periodo
ORDER BY pn.año DESC, pn.mes DESC, e.apellidos, e.nombres;
```

#### Consulta 2: Detalle Completo de una Nómina

```sql
-- Detalle completo de nómina con bonos, beneficios y deducciones
SELECT 
    CONCAT(e.nombres, ' ', e.apellidos) AS empleado,
    'BONOS' AS categoria,
    db.tipo_bono AS concepto,
    db.monto
FROM nomina n
INNER JOIN empleado e ON n.id_empleado = e.id_empleado
INNER JOIN detalle_bono db ON n.id_nomina = db.id_nomina
WHERE n.id_nomina = 1

UNION ALL

SELECT 
    CONCAT(e.nombres, ' ', e.apellidos),
    'BENEFICIOS',
    dbe.tipo_beneficio,
    dbe.monto
FROM nomina n
INNER JOIN empleado e ON n.id_empleado = e.id_empleado
INNER JOIN detalle_beneficio dbe ON n.id_nomina = dbe.id_nomina
WHERE n.id_nomina = 1

UNION ALL

SELECT 
    CONCAT(e.nombres, ' ', e.apellidos),
    'DEDUCCIONES',
    dd.tipo_deduccion,
    dd.monto
FROM nomina n
INNER JOIN empleado e ON n.id_empleado = e.id_empleado
INNER JOIN detalle_deduccion dd ON n.id_nomina = dd.id_nomina
WHERE n.id_nomina = 1

ORDER BY categoria, concepto;
```

#### Consulta 3: Empleados Elegibles para Bonos

```sql
-- Empleados asalariados con más de 5 años (elegibles para bono antigüedad)
SELECT 
    e.numero_identificacion,
    CONCAT(e.nombres, ' ', e.apellidos) AS nombre_completo,
    e.fecha_ingreso,
    TIMESTAMPDIFF(YEAR, e.fecha_ingreso, CURDATE()) AS años_antiguedad,
    e.salario_base,
    ROUND(e.salario_base * 0.10, 2) AS bono_antiguedad
FROM empleado e
INNER JOIN tipo_empleado te ON e.id_tipo_empleado = te.id_tipo_empleado
WHERE te.nombre_tipo = 'ASALARIADO'
  AND TIMESTAMPDIFF(YEAR, e.fecha_ingreso, CURDATE()) >= 5
  AND e.estado = 'ACTIVO';
```

#### Consulta 4: Costo Total de Nómina por Período

```sql
-- Costo total de nómina por período
SELECT 
    CONCAT(pn.año, '-', LPAD(pn.mes, 2, '0')) AS periodo,
    COUNT(n.id_nomina) AS total_empleados,
    SUM(n.salario_bruto) AS total_salarios_bruto,
    SUM(n.total_bonos) AS total_bonos,
    SUM(n.total_beneficios) AS total_beneficios,
    SUM(n.total_deducciones) AS total_deducciones,
    SUM(n.salario_neto) AS total_nomina_neta
FROM periodo_nomina pn
LEFT JOIN nomina n ON pn.id_periodo = n.id_periodo
WHERE pn.id_periodo = 1
GROUP BY pn.id_periodo, pn.año, pn.mes;
```

---

## Diagrama de Relaciones (Descripción Textual)

```
tipo_empleado (1) -----> (N) empleado
empleado (1) -----> (N) nomina
periodo_nomina (1) -----> (N) nomina
nomina (1) -----> (N) detalle_bono
nomina (1) -----> (N) detalle_beneficio
nomina (1) -----> (N) detalle_deduccion
nomina (1) -----> (N) auditoria_nomina
```

**Relaciones:**
- Un tipo de empleado puede tener muchos empleados
- Un empleado puede tener muchas nóminas (una por período)
- Un período puede tener muchas nóminas (una por empleado)
- Una nómina puede tener múltiples bonos, beneficios y deducciones

---

## Notas Importantes

1. **Principio de Responsabilidad Única**: Cada tabla tiene una responsabilidad clara
2. **Normalización**: El modelo está en 3FN (Tercera Forma Normal)
3. **Integridad Referencial**: Todas las relaciones están protegidas con FK
4. **Validaciones**: Los constraints garantizan reglas de negocio a nivel de BD
5. **Auditoría**: La tabla de auditoría permite trazabilidad completa
6. **Escalabilidad**: El diseño permite agregar nuevos tipos de empleado fácilmente
7. **Flexibilidad**: Los campos específicos (horas, ventas) están en la tabla nomina

Este modelo de base de datos proporciona una base sólida para implementar la lógica de negocio en el código orientado a objetos.