def test_get_service_providers(client):
    response = client.get("/service-providers/1")
    assert response.status_code == 200
    sp = response.json()
    assert sp["name"] == "droles-test"
    assert "id" in sp
    assert sp["id"] == 1


def test_get_service_provider_not_found(client):
    """Test retrieving a non-existent service provider."""
    # Use a very large ID that shouldn't exist
    response = client.get("/service-providers/99999")

    # This should return 404 if properly implemented
    assert response.status_code == 404
