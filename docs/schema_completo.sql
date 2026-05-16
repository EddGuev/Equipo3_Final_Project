-- ============================================
-- Script de Creación de Base de Datos SQLite
-- Proyecto: ChatDoc - Sistema de Chat con Documentos
-- Fecha: 2026-05-16
-- Autor: Equipo 3 - Ingeniería de Software
-- ============================================

-- Habilitar claves foráneas (importante en SQLite)
PRAGMA foreign_keys = ON;

-- ============================================
-- TABLA: usuarios
-- Descripción: Almacena información de usuarios registrados
-- ============================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Restricciones
    CONSTRAINT chk_username_length CHECK (LENGTH(username) >= 3),
    CONSTRAINT chk_username_format CHECK (username NOT LIKE '% %')
);

-- Índice para búsquedas rápidas por username
CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);

-- ============================================
-- TABLA: sesiones
-- Descripción: Registro de sesiones activas e históricas
-- ============================================
CREATE TABLE IF NOT EXISTS sesiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP NULL,
    activa BOOLEAN DEFAULT 1,

    -- Clave foránea
    CONSTRAINT fk_sesiones_usuario 
        FOREIGN KEY (usuario_id) 
        REFERENCES usuarios(id) 
        ON DELETE CASCADE,

    -- Restricciones
    CONSTRAINT chk_fecha_fin CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_inicio)
);

-- Índice para consultas de sesiones activas
CREATE INDEX IF NOT EXISTS idx_sesiones_activas ON sesiones(usuario_id, activa);

-- ============================================
-- TABLA: archivos
-- Descripción: Almacena información de archivos cargados
-- ============================================
CREATE TABLE IF NOT EXISTS archivos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    ruta TEXT,
    tipo TEXT NOT NULL,
    contenido TEXT,
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Restricciones
    CONSTRAINT chk_tipo_archivo CHECK (tipo IN ('TXT', 'PDF', 'JSON', 'XML')),
    CONSTRAINT chk_nombre_no_vacio CHECK (LENGTH(nombre) > 0)
);

-- Índice para búsquedas por tipo de archivo
CREATE INDEX IF NOT EXISTS idx_archivos_tipo ON archivos(tipo);
CREATE INDEX IF NOT EXISTS idx_archivos_fecha ON archivos(fecha_carga DESC);

-- ============================================
-- TABLA: conversaciones
-- Descripción: Almacena conversaciones entre usuario y sistema
-- ============================================
CREATE TABLE IF NOT EXISTS conversaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    archivo_id INTEGER NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    titulo TEXT DEFAULT 'Nueva conversación',

    -- Claves foráneas
    CONSTRAINT fk_conversaciones_usuario 
        FOREIGN KEY (usuario_id) 
        REFERENCES usuarios(id) 
        ON DELETE CASCADE,

    CONSTRAINT fk_conversaciones_archivo 
        FOREIGN KEY (archivo_id) 
        REFERENCES archivos(id) 
        ON DELETE SET NULL
);

-- Índices para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_conversaciones_usuario ON conversaciones(usuario_id);
CREATE INDEX IF NOT EXISTS idx_conversaciones_fecha ON conversaciones(fecha_creacion DESC);
CREATE INDEX IF NOT EXISTS idx_conversaciones_archivo ON conversaciones(archivo_id);

-- ============================================
-- TABLA: mensajes
-- Descripción: Almacena mensajes individuales de cada conversación
-- ============================================
CREATE TABLE IF NOT EXISTS mensajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversacion_id INTEGER NOT NULL,
    emisor TEXT NOT NULL,
    texto TEXT NOT NULL,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Clave foránea
    CONSTRAINT fk_mensajes_conversacion 
        FOREIGN KEY (conversacion_id) 
        REFERENCES conversaciones(id) 
        ON DELETE CASCADE,

    -- Restricciones
    CONSTRAINT chk_emisor CHECK (emisor IN ('usuario', 'sistema')),
    CONSTRAINT chk_texto_no_vacio CHECK (LENGTH(texto) > 0)
);

-- Índice para consultas de mensajes por conversación
CREATE INDEX IF NOT EXISTS idx_mensajes_conversacion ON mensajes(conversacion_id, fecha_hora);

-- ============================================
-- VISTAS ÚTILES
-- ============================================

-- Vista: Conversaciones con información completa
CREATE VIEW IF NOT EXISTS v_conversaciones_completas AS
SELECT 
    c.id AS conversacion_id,
    c.titulo,
    c.fecha_creacion,
    u.username AS usuario,
    a.nombre AS archivo_nombre,
    a.tipo AS archivo_tipo,
    COUNT(m.id) AS total_mensajes
FROM conversaciones c
INNER JOIN usuarios u ON c.usuario_id = u.id
LEFT JOIN archivos a ON c.archivo_id = a.id
LEFT JOIN mensajes m ON c.id = m.conversacion_id
GROUP BY c.id, c.titulo, c.fecha_creacion, u.username, a.nombre, a.tipo;

-- Vista: Últimas conversaciones por usuario
CREATE VIEW IF NOT EXISTS v_ultimas_conversaciones AS
SELECT 
    u.id AS usuario_id,
    u.username,
    c.id AS conversacion_id,
    c.titulo,
    c.fecha_creacion,
    MAX(m.fecha_hora) AS ultimo_mensaje
FROM usuarios u
INNER JOIN conversaciones c ON u.id = c.usuario_id
LEFT JOIN mensajes m ON c.id = m.conversacion_id
GROUP BY u.id, u.username, c.id, c.titulo, c.fecha_creacion
ORDER BY ultimo_mensaje DESC;

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger: Actualizar título de conversación con primer mensaje
CREATE TRIGGER IF NOT EXISTS trg_actualizar_titulo_conversacion
AFTER INSERT ON mensajes
FOR EACH ROW
WHEN (SELECT titulo FROM conversaciones WHERE id = NEW.conversacion_id) = 'Nueva conversación'
BEGIN
    UPDATE conversaciones 
    SET titulo = SUBSTR(NEW.texto, 1, 50) || CASE 
        WHEN LENGTH(NEW.texto) > 50 THEN '...' 
        ELSE '' 
    END
    WHERE id = NEW.conversacion_id;
END;

-- Trigger: Cerrar sesión automáticamente al crear nueva
CREATE TRIGGER IF NOT EXISTS trg_cerrar_sesiones_anteriores
AFTER INSERT ON sesiones
FOR EACH ROW
BEGIN
    UPDATE sesiones 
    SET activa = 0, 
        fecha_fin = CURRENT_TIMESTAMP
    WHERE usuario_id = NEW.usuario_id 
      AND id != NEW.id 
      AND activa = 1;
END;

-- ============================================
-- DATOS DE PRUEBA (OPCIONAL - Comentar en producción)
-- ============================================

-- Usuario de prueba
INSERT OR IGNORE INTO usuarios (username, password_hash) 
VALUES ('admin', 'pbkdf2:sha256:260000$test$hash');

INSERT OR IGNORE INTO usuarios (username, password_hash) 
VALUES ('usuario_demo', 'pbkdf2:sha256:260000$demo$hash');

-- ============================================
-- CONSULTAS DE VERIFICACIÓN
-- ============================================

-- Verificar estructura de tablas
-- SELECT name, sql FROM sqlite_master WHERE type='table';

-- Verificar índices
-- SELECT name, tbl_name FROM sqlite_master WHERE type='index';

-- Verificar vistas
-- SELECT name FROM sqlite_master WHERE type='view';

-- Verificar triggers
-- SELECT name FROM sqlite_master WHERE type='trigger';

-- ============================================
-- FIN DEL SCRIPT
-- ============================================
