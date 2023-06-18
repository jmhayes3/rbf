def test_main_route(test_client):
    response = test_client.get("/")
    assert response.status_code == 200


def test_auth_route(test_client):
    response = test_client.get("/auth/login")
    assert response.status_code == 200
