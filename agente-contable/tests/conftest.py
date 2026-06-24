"""Fixtures compartidas para toda la suite de tests."""
from __future__ import annotations

import pytest

import config
import database.db as db_module
from tools.db_tools import tool_upsert_factura


@pytest.fixture(autouse=True)
def _patch_empresa(monkeypatch):
    """Asegura valores de empresa válidos en todos los tests."""
    monkeypatch.setattr(config, "EMPRESA_NIF",      "B12345678")
    monkeypatch.setattr(config, "EMPRESA_NOMBRE",   "EasyTic Test SL")
    monkeypatch.setattr(config, "EMPRESA_EJERCICIO", 2025)


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    """BD SQLite temporal aislada; resetea el singleton _conn entre tests."""
    monkeypatch.setattr(config, "DB_PATH", str(tmp_path / "test.db"))
    db_module._conn = None
    db_module.get_conn()
    yield
    db_module._conn.close()
    db_module._conn = None


@pytest.fixture
def seeded_db(tmp_db):
    """tmp_db + facturas representativas en los 4 trimestres de 2025."""
    facturas = [
        # Q1 — emitida 21%, con retención
        {"tipo": "emitida",  "fecha": "2025-02-15", "base_imponible": 3000.0, "tipo_iva": 21,
         "cuota_iva": 630.0, "tipo_retencion": 15.0, "cuota_retencion": 450.0, "total": 3180.0,
         "fuente": "test", "fuente_id": "q1e1", "nif_emisor": "B12345678",
         "nombre_emisor": "EasyTic Test SL", "nif_receptor": "A11111111",
         "nombre_receptor": "Cliente A", "numero": "F/2025/001", "concepto": "Consultoría Q1"},
        # Q1 — recibida, retención profesional
        {"tipo": "recibida", "fecha": "2025-03-10", "base_imponible": 800.0, "tipo_iva": 21,
         "cuota_iva": 168.0, "tipo_retencion": 15.0, "cuota_retencion": 120.0, "total": 848.0,
         "fuente": "test", "fuente_id": "q1r1", "nif_emisor": "A22222222",
         "nombre_emisor": "Freelance Juan", "nif_receptor": "B12345678",
         "nombre_receptor": "EasyTic Test SL", "numero": "FR-01", "concepto": "Diseño"},
        # Q2 — emitida 10%
        {"tipo": "emitida",  "fecha": "2025-05-20", "base_imponible": 2000.0, "tipo_iva": 10,
         "cuota_iva": 200.0, "tipo_retencion": 0.0,  "cuota_retencion": 0.0,   "total": 2200.0,
         "fuente": "test", "fuente_id": "q2e1", "nif_emisor": "B12345678",
         "nombre_emisor": "EasyTic Test SL", "nif_receptor": "B33333333",
         "nombre_receptor": "Cliente B", "numero": "F/2025/002", "concepto": "Diseño web"},
        # Q3 — recibida, segunda freelance
        {"tipo": "recibida", "fecha": "2025-08-01", "base_imponible": 600.0, "tipo_iva": 21,
         "cuota_iva": 126.0, "tipo_retencion": 15.0, "cuota_retencion": 90.0, "total": 636.0,
         "fuente": "test", "fuente_id": "q3r1", "nif_emisor": "A33333333",
         "nombre_emisor": "Freelance Ana", "nif_receptor": "B12345678",
         "nombre_receptor": "EasyTic Test SL", "numero": "FR-02", "concepto": "Redacción"},
        # Q4 — emitida 21%, gran proyecto
        {"tipo": "emitida",  "fecha": "2025-11-05", "base_imponible": 5000.0, "tipo_iva": 21,
         "cuota_iva": 1050.0, "tipo_retencion": 15.0, "cuota_retencion": 750.0, "total": 5300.0,
         "fuente": "test", "fuente_id": "q4e1", "nif_emisor": "B12345678",
         "nombre_emisor": "EasyTic Test SL", "nif_receptor": "B44444444",
         "nombre_receptor": "Cliente C", "numero": "F/2025/003", "concepto": "SEO anual"},
        # Q4 — recibida sin retención (proveedor sociedad)
        {"tipo": "recibida", "fecha": "2025-12-01", "base_imponible": 1200.0, "tipo_iva": 21,
         "cuota_iva": 252.0, "tipo_retencion": 0.0,  "cuota_retencion": 0.0,   "total": 1452.0,
         "fuente": "test", "fuente_id": "q4r1", "nif_emisor": "B55555555",
         "nombre_emisor": "Proveedor SL", "nif_receptor": "B12345678",
         "nombre_receptor": "EasyTic Test SL", "numero": "P-100", "concepto": "Servidores"},
    ]
    for f in facturas:
        tool_upsert_factura(f)
