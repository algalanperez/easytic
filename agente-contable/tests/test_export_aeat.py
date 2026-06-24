"""Tests de exportación XML/JSON/CSV (tools/export_aeat.py)."""
from __future__ import annotations

import pytest

from tools.export_aeat import (
    export_303_xml, export_111_xml, export_390_xml, export_190_xml,
    export_200_json, export_facturas_csv, export_model,
)


class TestExport303Xml:
    def test_contiene_raiz_correcta(self, tmp_db):
        xml = export_303_xml(2025, "Q1")
        assert "<T30300>" in xml

    def test_contiene_casillas_principales(self, tmp_db):
        xml = export_303_xml(2025, "Q1")
        assert "<C27_TotalDevengado>" in xml
        assert "<C46_TotalDeducible>" in xml
        assert "<C64_Resultado>" in xml

    def test_incluye_nif_empresa(self, tmp_db):
        xml = export_303_xml(2025, "Q1")
        assert "B12345678" in xml

    def test_es_xml_valido(self, tmp_db):
        import xml.etree.ElementTree as ET
        xml = export_303_xml(2025, "Q1")
        ET.fromstring(xml.split("\n", 1)[1])  # salta la declaración XML


class TestExport111Xml:
    def test_contiene_raiz_correcta(self, tmp_db):
        xml = export_111_xml(2025, "Q1")
        assert "<T11100>" in xml

    def test_contiene_perceptores(self, tmp_db):
        xml = export_111_xml(2025, "Q1")
        assert "<C10_Perceptores>" in xml


class TestExport390Xml:
    def test_contiene_raiz_correcta(self, tmp_db):
        xml = export_390_xml(2025)
        assert "<T39000>" in xml

    def test_contiene_desglose_trimestral(self, seeded_db):
        xml = export_390_xml(2025)
        assert "<DesgloseTrimestral>" in xml
        assert "<Trimestre_Q1>" in xml
        assert "<Trimestre_Q4>" in xml

    def test_contiene_resultado_final(self, tmp_db):
        xml = export_390_xml(2025)
        assert "<C71_ResultadoFinal>" in xml


class TestExport190Xml:
    def test_contiene_raiz_correcta(self, tmp_db):
        xml = export_190_xml(2025)
        assert "<T19000>" in xml

    def test_contiene_bloque_perceptores(self, seeded_db):
        xml = export_190_xml(2025)
        assert "<Perceptores>" in xml

    def test_perceptores_con_datos(self, seeded_db):
        xml = export_190_xml(2025)
        assert "<Clave>G</Clave>" in xml
        assert "<BaseRetencion>" in xml


class TestExportModel:
    def test_303_genera_xml(self, tmp_db, tmp_path):
        r = export_model("303", 2025, "Q1", output_path=str(tmp_path / "out.xml"))
        assert r["formato"] == "xml"
        assert r["bytes"] > 0

    def test_390_genera_xml(self, tmp_db, tmp_path):
        r = export_model("390", 2025, output_path=str(tmp_path / "out.xml"))
        assert r["formato"] == "xml"

    def test_190_genera_xml(self, tmp_db, tmp_path):
        r = export_model("190", 2025, output_path=str(tmp_path / "out.xml"))
        assert r["formato"] == "xml"

    def test_200_genera_json(self, tmp_db, tmp_path):
        r = export_model("200", 2025, output_path=str(tmp_path / "out.json"))
        assert r["formato"] == "json"

    def test_modelo_invalido_lanza_error(self, tmp_db, tmp_path):
        with pytest.raises(ValueError):
            export_model("999", 2025, output_path=str(tmp_path / "out.xml"))


class TestExportFacturasCsv:
    def test_sin_facturas_devuelve_vacio(self, tmp_db):
        csv = export_facturas_csv("2025-01-01", "2025-12-31")
        assert csv == ""

    def test_con_facturas_incluye_cabecera(self, seeded_db):
        csv = export_facturas_csv("2025-01-01", "2025-12-31")
        assert "base_imponible" in csv
        assert "tipo_iva" in csv

    def test_filtro_por_tipo(self, seeded_db):
        csv_emit = export_facturas_csv("2025-01-01", "2025-12-31", tipo="emitida")
        assert "recibida" not in csv_emit
