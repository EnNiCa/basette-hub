-- ============================================================
-- BASETTE HUB - Esquema de base de datos
-- ============================================================

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dni VARCHAR(15),
    nombre VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'jefe_equipo', 'comercial') NOT NULL DEFAULT 'comercial',
    jefe_id INT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_alta DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (jefe_id) REFERENCES usuarios(id)
);

CREATE TABLE canales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL
);

CREATE TABLE companias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    tipo_servicio ENUM('energia', 'alarmas', 'telefonia', 'placas_solares') NOT NULL 
);

CREATE TABLE tarifas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    compania_id INT NOT NULL,
    nombre VARCHAR(120) NOT NULL,
    tipo_servicio ENUM('energia', 'alarmas', 'telefonia', 'placas_solares') NOT NULL,
    condiciones TEXT,
    vigente BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (compania_id) REFERENCES companias(id)
);

CREATE TABLE leads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_cliente VARCHAR(160) NOT NULL,
    telefono VARCHAR(30),
    canal_id INT,
    comercial_id INT NOT NULL,
    estado ENUM('nuevo', 'contactado', 'convertido', 'descartado') DEFAULT 'nuevo',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (canal_id) REFERENCES canales(id),
    FOREIGN KEY (comercial_id) REFERENCES usuarios(id)
);

CREATE TABLE ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lead_id INT,
    comercial_id INT NOT NULL,
    modulo ENUM('energia', 'alarmas', 'telefonia', 'placas_solares') NOT NULL,
    tipo_energia ENUM('luz', 'gas'),
    compania_id INT NOT NULL,
    tarifa_id INT NOT NULL,
    canal_id INT,
    nombre VARCHAR(120),
    apellidos VARCHAR(150),
    tipo_cliente ENUM('particular', 'empresa') NOT NULL DEFAULT 'particular',
    direccion VARCHAR(255),
    cp VARCHAR(5),
    dni VARCHAR(15),
    cif VARCHAR(15),
    razon_social VARCHAR(150),
    cups VARCHAR(30),
    telefono VARCHAR(30),
    email VARCHAR(160),
    numero_cuenta VARCHAR(34),
    fecha_firma DATE,
    fecha_activacion DATE,
    fecha_liquidacion DATE,
    fecha_descomision DATE,
    importe_liquidar DECIMAL(10,2),
    importe_descomisionado DECIMAL(10,2),
    mantenimiento BOOLEAN NOT NULL DEFAULT FALSE,
    bateria BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_pago_comercial DATE,
    importe_pago_comercial DECIMAL(10,2),
    fecha_descomision_comercial DATE,
    importe_descomisionado_comercial DECIMAL(10,2),
    observaciones TEXT,
    estado ENUM('nulo','pendiente_carga','pendiente_firma','scoring','activacion','activa','incidencia','baja') NOT NULL DEFAULT 'nulo',
    FOREIGN KEY (lead_id) REFERENCES leads(id),
    FOREIGN KEY (comercial_id) REFERENCES usuarios(id),
    FOREIGN KEY (compania_id) REFERENCES companias(id),
    FOREIGN KEY (tarifa_id) REFERENCES tarifas(id),
    FOREIGN KEY (canal_id) REFERENCES canales(id)
);

CREATE TABLE venta_archivos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT NOT NULL,
    categoria ENUM('dni','certificado_bancario','escritura','justo_titulo','cif','facturas','acta_comunidad','otros') NOT NULL DEFAULT 'otros',
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (venta_id) REFERENCES ventas(id)
);

CREATE TABLE contratos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT NOT NULL,
    numero_contrato VARCHAR(60) NOT NULL,
    estado ENUM('pendiente', 'activo', 'cancelado') DEFAULT 'pendiente',
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (venta_id) REFERENCES ventas(id)
);

CREATE TABLE contrato_historial (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contrato_id INT NOT NULL,
    estado_anterior VARCHAR(30),
    estado_nuevo VARCHAR(30) NOT NULL,
    modificado_por INT,
    fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contrato_id) REFERENCES contratos(id),
    FOREIGN KEY (modificado_por) REFERENCES usuarios(id)
);

CREATE TABLE incidencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT,
    comercial_id INT NOT NULL,
    descripcion TEXT NOT NULL,
    estado ENUM('abierta', 'en_proceso', 'cerrada') DEFAULT 'abierta',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (venta_id) REFERENCES ventas(id),
    FOREIGN KEY (comercial_id) REFERENCES usuarios(id)
);

CREATE TABLE liquidaciones_comerciales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comercial_id INT NOT NULL,
    periodo VARCHAR(7) NOT NULL,
    importe DECIMAL(10,2) NOT NULL,
    estado ENUM('pendiente', 'pagada') DEFAULT 'pendiente',
    FOREIGN KEY (comercial_id) REFERENCES usuarios(id)
);

CREATE TABLE liquidaciones_companias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    compania_id INT NOT NULL,
    periodo VARCHAR(7) NOT NULL,
    importe DECIMAL(10,2) NOT NULL,
    estado ENUM('pendiente', 'pagada') DEFAULT 'pendiente',
    FOREIGN KEY (compania_id) REFERENCES companias(id)
);

CREATE TABLE renovaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT NOT NULL,
    fecha_renovacion DATE NOT NULL,
    estado ENUM('pendiente', 'renovada', 'rechazada') DEFAULT 'pendiente',
    FOREIGN KEY (venta_id) REFERENCES ventas(id)
);

CREATE TABLE bajas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT NOT NULL,
    motivo TEXT,
    fecha_baja DATE NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES ventas(id)
);

CREATE TABLE actualizaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(160) NOT NULL,
    descripcion TEXT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE repositorios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(160) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    categoria VARCHAR(80),
    fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE noticias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(160) NOT NULL,
    contenido TEXT NOT NULL,
    fecha_publicacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    activa BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE incidencia_archivos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    incidencia_id INT NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incidencia_id) REFERENCES incidencias(id)
);

CREATE TABLE usuario_bajas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    fecha_baja DATE NOT NULL,
    fecha_reincorporacion DATE NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);