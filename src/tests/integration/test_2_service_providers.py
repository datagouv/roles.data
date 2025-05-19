def test_get_service_provider(client):
    response = client.get("/service-providers/info")
    assert response.status_code == 200
    sp = response.json()
    assert sp["name"] == "droles-test"
    assert "id" in sp
    assert sp["id"] == 1
