def test_upload_and_read_skill(client, valid_skill_zip):
    response = client.post(
        "/api/skills",
        files={"file": ("skill.zip", valid_skill_zip, "application/zip")},
    )
    assert response.status_code == 201
    skill = response.json()
    assert skill["name"] == "sample-review"
    assert len(skill["sha256"]) == 64

    retrieved = client.get(f"/api/skills/{skill['skill_id']}")
    assert retrieved.status_code == 200
    assert retrieved.json() == skill


def test_upload_rejects_zip_slip(client, malicious_zip):
    response = client.post(
        "/api/skills",
        files={"file": ("bad.zip", malicious_zip, "application/zip")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Archive contains an unsafe path"


def test_upload_rejects_non_zip(client):
    response = client.post(
        "/api/skills",
        files={"file": ("skill.txt", b"not a zip", "text/plain")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Upload must be a valid ZIP archive"

