def test_create_get_revoke_api_key(client, test_db):
    response = client.post("/api-keys/", json={
        "user_id": 1,
        "scopes": "read",
        "usage_limit": 100
    })
    assert response.status_code == 200
    api_key = response.json()
    assert api_key["scopes"] == "read"

    response = client.get("/api-keys/")
    assert response.status_code == 200
    keys = response.json()
    assert len(keys) > 0

    key_id = api_key["id"]
    response = client.delete(f"/api-keys/{key_id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "API key revoked successfully"