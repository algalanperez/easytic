"""Tests del panel web FastAPI (web/app.py)."""
from __future__ import annotations

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

import config


@pytest.fixture
def client(tmp_db, monkeypatch):
    """TestClient con auth desactivada y scheduler mockeado."""
    monkeypatch.setattr(config, "WEB_USER", "")
    monkeypatch.setattr(config, "WEB_PASS", "")
    with patch("scheduler.start"), patch("scheduler.stop"), patch("scheduler.list_jobs", return_value=[]):
        from web.app import app
        yield TestClient(app, raise_server_exceptions=True)


@pytest.fixture
def client_auth(tmp_db, monkeypatch):
    """TestClient con HTTP Basic Auth activada (user=admin, pass=test)."""
    monkeypatch.setattr(config, "WEB_USER", "admin")
    monkeypatch.setattr(config, "WEB_PASS", "test1234")
    with patch("scheduler.start"), patch("scheduler.stop"), patch("scheduler.list_jobs", return_value=[]):
        from web.app import app
        yield TestClient(app, raise_server_exceptions=True)


class TestRutasPublicas:
    def test_dashboard_ok(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "EasyTic Test SL" in r.text

    def test_facturas_ok(self, client):
        r = client.get("/facturas")
        assert r.status_code == 200

    def test_modelos_ok(self, client):
        r = client.get("/modelos")
        assert r.status_code == 200

    def test_sii_ok(self, client):
        r = client.get("/sii")
        assert r.status_code == 200

    def test_scheduler_ok(self, client):
        r = client.get("/scheduler")
        assert r.status_code == 200

    def test_sii_con_rango_ok(self, client):
        r = client.get("/sii?desde=2025-01-01&hasta=2025-12-31")
        assert r.status_code == 200


class TestAutenticacion:
    def test_sin_credenciales_401(self, client_auth):
        r = client_auth.get("/")
        assert r.status_code == 401
        assert "WWW-Authenticate" in r.headers

    def test_password_incorrecta_401(self, client_auth):
        r = client_auth.get("/", auth=("admin", "wrong"))
        assert r.status_code == 401

    def test_credenciales_correctas_200(self, client_auth):
        r = client_auth.get("/", auth=("admin", "test1234"))
        assert r.status_code == 200

    def test_todas_las_rutas_protegidas(self, client_auth):
        for path in ["/", "/facturas", "/modelos", "/sii", "/scheduler"]:
            r = client_auth.get(path)
            assert r.status_code == 401, f"{path} debería devolver 401"

    def test_sin_web_user_acceso_libre(self, client):
        # client fixture tiene WEB_USER="" → sin auth
        r = client.get("/")
        assert r.status_code == 200


class TestAccionesModelos:
    def test_calcular_303_redirige(self, client):
        r = client.post("/modelos/calcular", data={"modelo": "303", "periodo": "Q1", "ejercicio": "2025"})
        assert r.status_code in (200, 303)

    def test_calcular_390_redirige(self, client):
        r = client.post("/modelos/calcular", data={"modelo": "390", "periodo": "anual", "ejercicio": "2025"})
        assert r.status_code in (200, 303)

    def test_download_303_xml(self, client):
        r = client.get("/modelos/download/303/2025/Q1")
        assert r.status_code == 200
        assert b"T30300" in r.content

    def test_download_390_xml(self, client):
        r = client.get("/modelos/download/390/2025/anual")
        assert r.status_code == 200
        assert b"T39000" in r.content

    def test_download_190_xml(self, client):
        r = client.get("/modelos/download/190/2025/anual")
        assert r.status_code == 200
        assert b"T19000" in r.content

    def test_presentar_borrador(self, client):
        # Crear borrador primero
        client.post("/modelos/calcular", data={"modelo": "303", "periodo": "Q1", "ejercicio": "2025"})
        r = client.post("/modelos/presentar", data={"modelo": "303", "periodo": "Q1", "ejercicio": "2025"})
        assert r.status_code in (200, 303)

    def test_presentar_inexistente_no_falla(self, client):
        r = client.post("/modelos/presentar", data={"modelo": "303", "periodo": "Q4", "ejercicio": "2025"})
        assert r.status_code in (200, 303)


class TestExportaciones:
    def test_export_csv_facturas(self, client):
        r = client.post("/facturas/exportar", data={"desde": "2025-01-01", "hasta": "2025-12-31", "tipo": ""})
        assert r.status_code == 200

    def test_export_csv_sin_fechas_redirige(self, client):
        r = client.post("/facturas/exportar", data={"desde": "", "hasta": "", "tipo": ""})
        assert r.status_code in (200, 303)
