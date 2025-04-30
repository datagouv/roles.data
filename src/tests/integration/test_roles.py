def test_add_roles(client):
    response = client.get("/roles/")
    assert response.status_code == 200
    roles = response.json()
    assert len(roles) == 2

    response = client.post(
        "/roles/", json={"role_name": f"user_{len(roles)}", "is_admin": False}
    )
    assert response.status_code == 201

    response = client.get("/roles/")
    assert response.status_code == 200
    roles = response.json()
    assert len(roles) == 3
    assert roles[-1]["role_name"] == "manager"


async def test_get_roles_by_id(client):
    response = client.get("/roles/1")
    assert response.status_code == 200
    role = response.json()
    assert role["role_name"] == "admin"
    assert role["is_admin"] is True

    response = client.get("/roles/999")
    assert response.status_code == 404
