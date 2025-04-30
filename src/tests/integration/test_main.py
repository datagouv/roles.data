def test_health_check(client):
    response = client.get("/health/")
    assert response.status_code == 200

    json = response.json()
    assert json["status"] == "healthy"
    assert json["database"] == "connected"
