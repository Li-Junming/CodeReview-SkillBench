from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_health_does_not_require_api_key(tmp_path, public_root, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = TestClient(create_app(data_root=tmp_path, project_root=public_root))
    assert client.get("/api/health").json() == {
        "status": "ok",
        "version": "0.1.0-beta",
    }

