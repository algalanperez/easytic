"""Tests de verificación SII/Verifactu (tools/sii_check.py)."""
from __future__ import annotations

import pytest

from tools.db_tools import tool_upsert_factura
from tools.sii_check import check_sii_compliance


def _factura(**overrides):
    base = {
        "tipo": "emitida", "fecha": "2025-06-01",
        "base_imponible": 1000.0, "tipo_iva": 21, "cuota_iva": 210.0,
        "tipo_retencion": 0.0, "cuota_retencion": 0.0, "total": 1210.0,
        "fuente": "test", "fuente_id": "sii_ok",
        "nif_emisor": "B12345678", "nombre_emisor": "EasyTic SL",
        "nif_receptor": "A11111111", "nombre_receptor": "Cliente Test",
        "numero": "F/SII/01", "concepto": "Servicio",
    }
    return {**base, **overrides}


class TestSiiCompliance:
    def test_sin_facturas_100_pct(self, tmp_db):
        r = check_sii_compliance("2025-01-01", "2025-12-31")
        assert r["resumen"]["total_facturas"] == 0
        assert r["resumen"]["porcentaje_cumplimiento"] == 100

    def test_factura_valida_pasa(self, tmp_db):
        tool_upsert_factura(_factura())
        r = check_sii_compliance("2025-01-01", "2025-12-31")
        assert r["resumen"]["facturas_ok"] == 1
        assert r["resumen"]["facturas_con_errores"] == 0

    def test_nif_invalido_falla(self, tmp_db):
        # NIF con caracteres no alfanuméricos — falla la regex ^[A-Z0-9]{8,9}[A-Z0-9]$
        tool_upsert_factura(_factura(fuente_id="nif_mal", nif_emisor="B12-INVALIDO!"))
        r = check_sii_compliance("2025-01-01", "2025-12-31")
        assert r["resumen"]["facturas_con_errores"] == 1
        errores = r["facturas_error"][0]["errores"]
        assert any("NIF" in e for e in errores)

    def test_tipo_iva_invalido_falla(self, tmp_db):
        tool_upsert_factura(_factura(fuente_id="iva_malo", tipo_iva=13, cuota_iva=130.0, total=1130.0))
        r = check_sii_compliance("2025-01-01", "2025-12-31")
        assert r["resumen"]["facturas_con_errores"] == 1

    def test_total_inconsistente_falla(self, tmp_db):
        # total correcto sería 1210, ponemos 9999
        tool_upsert_factura(_factura(fuente_id="total_mal", total=9999.0))
        r = check_sii_compliance("2025-01-01", "2025-12-31")
        assert r["resumen"]["facturas_con_errores"] == 1

    def test_filtro_por_tipo(self, tmp_db):
        tool_upsert_factura(_factura(fuente_id="emit1", tipo="emitida"))
        tool_upsert_factura(_factura(fuente_id="recv1", tipo="recibida"))
        r = check_sii_compliance("2025-01-01", "2025-12-31", tipo="emitida")
        assert r["resumen"]["total_facturas"] == 1

    def test_estructura_respuesta(self, tmp_db):
        r = check_sii_compliance("2025-01-01", "2025-12-31")
        assert "resumen" in r
        assert "facturas_error" in r
        assert "facturas_ok_ids" in r
        assert "recomendaciones" in r
        res = r["resumen"]
        assert all(k in res for k in (
            "total_facturas", "facturas_ok", "facturas_con_errores", "porcentaje_cumplimiento"
        ))
