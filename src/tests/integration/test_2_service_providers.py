def test_get_service_provider(client):
    response = client.get("/service-providers/info")
    assert response.status_code == 200
    sp = response.json()
    assert sp["name"] == "droles-test"
    assert "id" in sp
    assert sp["id"] == 1


def test_get_all_service_providers(client):
    """Test retrieving all service providers"""
    # Use a very large ID that shouldn't exist
    response = client.get("/service-providers/")

    assert response.status_code == 200
    sps = response.json()
    assert isinstance(sps, list)
    assert len(sps) == 1

    sp = sps[0]

    assert sp["name"] == "droles-test"
    assert "id" in sp
    assert sp["id"] == 1
