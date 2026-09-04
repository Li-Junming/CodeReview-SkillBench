def test_offline_run_completes_and_exposes_report(client):
    response = client.post("/api/runs", json={"profile": "offline-demo"})
    assert response.status_code == 201
    run = response.json()
    assert run["status"] == "COMPLETED"

    status = client.get(f"/api/runs/{run['run_id']}")
    assert status.status_code == 200
    assert status.json() == run

    report = client.get(f"/api/runs/{run['run_id']}/report")
    assert report.status_code == 200
    assert report.json()["report_type"] == "PUBLIC_OFFLINE_DEMO"


def test_live_run_without_provider_configuration_is_rejected(client, monkeypatch):
    monkeypatch.delenv("SKILLBENCH_PROVIDER", raising=False)
    response = client.post("/api/runs", json={"profile": "development"})
    assert response.status_code == 422
    assert response.json()["detail"] == "Live provider is not configured"
