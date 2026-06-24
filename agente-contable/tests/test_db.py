"""Tests de la capa de acceso a datos (database/db.py)."""
from __future__ import annotations

import pytest

import database.db as db
from tools.db_tools import tool_upsert_factura

_FACTURA = {
    "tipo": "emitida", "fecha": "2025-06-01", "base_imponible": 1000.0,
    "tipo_iva": 21, "cuota_iva": 210.0, "tipo_retencion": 0.0,
    "cuota_retencion": 0.0, "total": 1210.0, "fuente": "test",
    "fuente_id": "f1", "nif_emisor": "B12345678", "nombre_emisor": "EasyTic SL",
    "nif_receptor": "A11111111", "nombre_receptor": "Cliente", "numero": "F/1",
    "concepto": "Test",
}


class TestUpsertFactura:
    def test_insert_devuelve_id(self, tmp_db):
        result = tool_upsert_factura(_FACTURA)
        # tool_upsert_factura devuelve {"ok": True, "id": "<24-char hash>"}
        assert isinstance(result, dict)
        assert result["ok"] is True
        assert isinstance(result["id"], str) and len(result["id"]) == 24

    def test_upsert_idempotente(self, tmp_db):
        r1 = tool_upsert_factura(_FACTURA)
        r2 = tool_upsert_factura(_FACTURA)
        assert r1["id"] == r2["id"]
        rows = db.query_facturas()
        assert len(rows) == 1

    def test_update_modifica_campos(self, tmp_db):
        # El ID se basa en fuente+fuente_id+fecha+total.
        # Para que sea el mismo registro, actualizamos solo concepto (no afecta al hash).
        tool_upsert_factura(_FACTURA)
        updated = {**_FACTURA, "concepto": "Concepto actualizado"}
        tool_upsert_factura(updated)
        rows = db.query_facturas()
        assert len(rows) == 1
        assert rows[0]["concepto"] == "Concepto actualizado"

    def test_genera_asientos_iva(self, tmp_db):
        tool_upsert_factura(_FACTURA)
        asientos = db.raw_query("SELECT * FROM asientos")
        # emitida con IVA > 0 → debe generar asiento 477
        assert any(a["cuenta"] == "477" for a in asientos)

    def test_raw_query_bloquea_escritura(self, tmp_db):
        with pytest.raises(ValueError, match="sólo admite SELECT"):
            db.raw_query("DELETE FROM facturas")


class TestMarkPresentado:
    def test_borrador_a_presentado(self, tmp_db):
        db.upsert_liquidacion("303", 2025, "Q1", {})
        assert db.mark_presentado("303", 2025, "Q1") is True
        rows = db.list_liquidaciones()
        assert rows[0]["estado"] == "presentado"
        assert rows[0]["presentado_en"] is not None

    def test_idempotente_segunda_llamada(self, tmp_db):
        db.upsert_liquidacion("303", 2025, "Q1", {})
        db.mark_presentado("303", 2025, "Q1")
        assert db.mark_presentado("303", 2025, "Q1") is False

    def test_inexistente_devuelve_false(self, tmp_db):
        assert db.mark_presentado("390", 2025, "anual") is False

    def test_solo_afecta_modelo_indicado(self, tmp_db):
        db.upsert_liquidacion("303", 2025, "Q1", {})
        db.upsert_liquidacion("111", 2025, "Q1", {})
        db.mark_presentado("303", 2025, "Q1")
        rows = {r["modelo"]: r for r in db.list_liquidaciones()}
        assert rows["303"]["estado"] == "presentado"
        assert rows["111"]["estado"] == "borrador"
