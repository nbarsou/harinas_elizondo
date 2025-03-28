-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS USUARIO (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    mail TEXT NOT NULL UNIQUE,
    contrasena TEXT NOT NULL,
    rol TEXT NOT NULL,
    nombre TEXT NOT NULL
);

-- Tabla de Clientes
CREATE TABLE IF NOT EXISTS CLIENTE (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    rfc TEXT,
    nombre_contacto TEXT,
    correo_contacto TEXT,
    requiere_certificado BOOLEAN NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT 1,
    contrasena TEXT NOT NULL,
    motivo_baja TEXT,
    configuracion_json TEXT
);

-- Tabla de Dirección del Cliente
CREATE TABLE IF NOT EXISTS DIRECCION_CLIENTE (
    id_direccion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    calle TEXT,
    num_exterior TEXT,
    num_interior TEXT,
    codigo_postal TEXT,
    delegacion TEXT,
    estado TEXT,
    FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id_cliente)
);

-- Tabla de Equipos de Laboratorio
CREATE TABLE IF NOT EXISTS EQUIPO_LABORATORIO (
    id_equipo INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    clave TEXT,
    marca TEXT,
    modelo TEXT,
    serie TEXT,
    descripcion_larga TEXT,
    descripcion_corta TEXT,
    proveedor TEXT,
    fecha_adquisicion TEXT,
    garantia TEXT,
    vigencia_garantia TEXT,
    ubicacion TEXT,
    encargado INTEGER,
    estado TEXT,
    causa_baja TEXT,
    FOREIGN KEY (encargado) REFERENCES USUARIO(id_usuario)
);

-- Tabla de Inspecciones
CREATE TABLE IF NOT EXISTS INSPECCION (
    id_inspeccion INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_lote TEXT NOT NULL,
    fecha TEXT NOT NULL,
    id_equipo INTEGER,
    secuencia TEXT,
    parametros_analizados TEXT,
    tipo_inspeccion TEXT,
    id_laboratorista INTEGER,
    FOREIGN KEY (id_equipo) REFERENCES EQUIPO_LABORATORIO(id_equipo),
    FOREIGN KEY (id_laboratorista) REFERENCES USUARIO(id_usuario)
);

-- Tabla de Certificados de Calidad
CREATE TABLE IF NOT EXISTS CERTIFICADO_CALIDAD (
    id_certificado INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    id_inspeccion INTEGER NOT NULL,
    secuencia_inspeccion TEXT,
    orden_compra TEXT,
    cantidad_solicitada REAL,
    cantidad_entregada REAL,
    numero_factura TEXT,
    fecha_envio TEXT,
    fecha_caducidad TEXT,
    resultados_analisis TEXT,
    compara_referencias TEXT,
    desviaciones TEXT,
    destinatario_correo TEXT,
    FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id_cliente),
    FOREIGN KEY (id_inspeccion) REFERENCES INSPECCION(id_inspeccion)
);

-- Tabla de Parámetros Analizados
CREATE TABLE IF NOT EXISTS PARAMETRO_ANALISIS (
    id_parametro INTEGER PRIMARY KEY AUTOINCREMENT,
    id_inspeccion INTEGER NOT NULL,
    id_equipo_laboratorio INTEGER NOT NULL,
    parametro_analizado TEXT NOT NULL,
    valor REAL,
    FOREIGN KEY (id_inspeccion) REFERENCES INSPECCION(id_inspeccion),
    FOREIGN KEY (id_equipo_laboratorio) REFERENCES EQUIPO_LABORATORIO(id_equipo)
);
