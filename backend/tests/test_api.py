from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "teachflow-api"}


def test_roadmap_preview_validates_input_but_does_not_fake_generation() -> None:
    response = client.post(
        "/api/v1/roadmaps/preview",
        json={"course_name": "Python Development", "learning_goals": ["Build APIs"]},
    )
    assert response.status_code == 503
    assert "no AI provider has been called" in response.json()["detail"]


def test_roadmap_preview_rejects_missing_course_name() -> None:
    response = client.post("/api/v1/roadmaps/preview", json={"description": "Python"})
    assert response.status_code == 422
