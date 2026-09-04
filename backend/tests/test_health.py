from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_health_does_not_require_api_key(tmp_path, public_root, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = TestClient(create_app(data_root=tmp_path, project_root=public_root))
    assert client.get("/api/health").json() == {
        "status": "ok",
        "version": "0.1.0-beta",
    }


def test_local_frontend_origin_is_allowed(client):
    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://127.0.0.1:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
