-- Facturas emitidas y recibidas
CREATE TABLE IF NOT EXISTS facturas (
    id            TEXT PRIMARY KEY,           -- hash SHA256 del contenido
    tipo          TEXT NOT NULL CHECK(tipo IN ('emitida','recibida')),
    numero        TEXT,
    fecha         TEXT NOT NULL,              -- ISO 8601: YYYY-MM-DD
    fecha_contable TEXT,
    nif_emisor    TEXT,
    nombre_emisor TEXT,
    nif_receptor  TEXT,
    nombre_receptor TEXT,
    base_imponible REAL NOT NULL DEFAULT 0,
    tipo_iva      REAL NOT NULL DEFAULT 21,   -- %
    cuota_iva     REAL NOT NULL DEFAULT 0,
    tipo_retencion REAL NOT NULL DEFAULT 0,   -- % IRPF
    cuota_retencion REAL NOT NULL DEFAULT 0,
    total         REAL NOT NULL DEFAULT 0,
    concepto      TEXT,
    fuente        TEXT,                       -- 'drive'|'gmail'|'easyfix'|'csv'
    fuente_id     TEXT,                       -- ID en la fuente original
    procesada     INTEGER NOT NULL DEFAULT 0, -- 1 = incluida en liquidación
    created_at    TEXT DEFAULT (datetime('now'))
);

-- Asientos contables simplificados (libro diario)
CREATE TABLE IF NOT EXISTS asientos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha         TEXT NOT NULL,
    concepto      TEXT NOT NULL,
    debe          REAL NOT NULL DEFAULT 0,
    haber         REAL NOT NULL DEFAULT 0,
    cuenta        TEXT,                       -- plan contable (ej. 477, 472)
    factura_id    TEXT REFERENCES facturas(id),
    created_at    TEXT DEFAULT (datetime('now'))
);

-- Liquidaciones fiscales generadas
CREATE TABLE IF NOT EXISTS liquidaciones (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    modelo        TEXT NOT NULL,              -- '303','111','200','390','190'
    ejercicio     INTEGER NOT NULL,
    periodo       TEXT NOT NULL,              -- 'Q1','Q2','Q3','Q4','anual'
    estado        TEXT DEFAULT 'borrador',    -- 'borrador'|'presentado'
    datos_json    TEXT,                       -- JSON con todos los campos del modelo
    presentado_en TEXT,
    created_at    TEXT DEFAULT (datetime('now')),
    UNIQUE(modelo, ejercicio, periodo)
);

-- Índices de rendimiento
CREATE INDEX IF NOT EXISTS idx_facturas_fecha   ON facturas(fecha);
CREATE INDEX IF NOT EXISTS idx_facturas_tipo    ON facturas(tipo);
CREATE INDEX IF NOT EXISTS idx_facturas_fuente  ON facturas(fuente, fuente_id);
CREATE INDEX IF NOT EXISTS idx_asientos_fecha   ON asientos(fecha);
