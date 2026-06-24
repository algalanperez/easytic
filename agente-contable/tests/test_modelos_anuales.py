"""Tests de Modelos 390, 190 y 200 (anuales)."""
from __future__ import annotations

from tools.modelo_390 import calculate_390
from tools.modelo_190 import calculate_190
from tools.modelo_200 import calculate_200


class TestCalculate390:
    def test_sin_facturas_todo_cero(self, tmp_db):
        r = calculate_390(2025)
        assert r["casillas"]["27_total_devengado"] == 0.0
        assert r["casillas"]["64_resultado_anual"] == 0.0
        assert r["casillas"]["71_resultado_final"] == 0.0

    def test_agrega_cuatro_trimestres(self, seeded_db):
        r = calculate_390(2025)
        assert len(r["trimestres"]) == 4
        assert set(r["trimestres"].keys()) == {"Q1", "Q2", "Q3", "Q4"}

    def test_base_general_anual_correcta(self, seeded_db):
        # emitidas 21%: Q1=3000, Q4=5000 → 8000
        r = calculate_390(2025)
        assert r["casillas"]["01_base_general"] == 8000.0

    def test_base_reducida_anual_correcta(self, seeded_db):
        # emitidas 10%: Q2=2000
        r = calculate_390(2025)
        assert r["casillas"]["03_base_reducido"] == 2000.0

    def test_resultado_anual_es_devengado_menos_deducible(self, seeded_db):
        r = calculate_390(2025)
        c = r["casillas"]
        esperado = round(c["27_total_devengado"] - c["46_total_deducible"], 2)
        assert c["64_resultado_anual"] == esperado

    def test_resultado_final_descuenta_suma_trimestral(self, seeded_db):
        r = calculate_390(2025)
        c = r["casillas"]
        esperado = round(c["66_resultado_estado"] - c["69_suma_trimestral"], 2)
        assert c["71_resultado_final"] == esperado

    def test_estructura_respuesta(self, tmp_db):
        r = calculate_390(2025)
        assert r["modelo"] == "390"
        assert r["periodo"] == "anual"
        assert "trimestres" in r and "resumen" in r


class TestCalculate190:
    def test_sin_retenciones_cero_perceptores(self, tmp_db):
        r = calculate_190(2025)
        assert r["casillas"]["n_perceptores"] == 0
        assert r["casillas"]["retenciones_total"] == 0.0
        assert r["perceptores"] == []

    def test_cuenta_perceptores_unicos(self, seeded_db):
        # Freelance Juan (Q1) + Freelance Ana (Q3) = 2
        r = calculate_190(2025)
        assert r["casillas"]["n_perceptores"] == 2

    def test_suma_retenciones_anuales(self, seeded_db):
        # Juan: 120 + Ana: 90 = 210
        r = calculate_190(2025)
        assert r["casillas"]["retenciones_total"] == 210.0

    def test_perceptores_tienen_clave_g(self, seeded_db):
        r = calculate_190(2025)
        for p in r["perceptores"]:
            assert p["clave"] == "G"

    def test_desglose_trimestral_completo(self, seeded_db):
        r = calculate_190(2025)
        assert set(r["trimestres"].keys()) == {"Q1", "Q2", "Q3", "Q4"}

    def test_advertencia_sin_nif(self, tmp_db):
        from tools.db_tools import tool_upsert_factura
        tool_upsert_factura({
            "tipo": "recibida", "fecha": "2025-05-01",
            "base_imponible": 500.0, "tipo_iva": 21, "cuota_iva": 105.0,
            "tipo_retencion": 15.0, "cuota_retencion": 75.0, "total": 530.0,
            "fuente": "test", "fuente_id": "sin_nif_x",
            "nif_emisor": None, "nombre_emisor": None,
            "nif_receptor": "B12345678", "nombre_receptor": "EasyTic SL",
            "numero": "X-01", "concepto": "Sin NIF",
        })
        r = calculate_190(2025)
        assert len(r["advertencias"]) > 0


class TestCalculate200:
    def test_sin_facturas_resultado_cero(self, tmp_db):
        r = calculate_200(2025)
        assert r["casillas"]["01_resultado_contable"] == 0.0
        assert r["casillas"]["621_cuota_diferencial"] == 0.0

    def test_ingresos_menos_gastos(self, seeded_db):
        r = calculate_200(2025)
        # ingresos = 3000+2000+5000=10000; gastos = 800+600+1200=2600
        assert r["inputs"]["ingresos"] == 10000.0
        assert r["inputs"]["gastos"] == 2600.0
        assert r["casillas"]["01_resultado_contable"] == 7400.0

    def test_tipo_gravamen_25(self, seeded_db):
        r = calculate_200(2025, tipo_gravamen=25.0)
        assert r["casillas"]["562_tipo_gravamen"] == 25.0

    def test_tipo_gravamen_personalizado(self, seeded_db):
        r = calculate_200(2025, tipo_gravamen=15.0)
        assert r["casillas"]["562_tipo_gravamen"] == 15.0

    def test_estructura_respuesta(self, tmp_db):
        r = calculate_200(2025)
        assert r["modelo"] == "200"
        assert r["periodo"] == "anual"
        assert "advertencias" in r
