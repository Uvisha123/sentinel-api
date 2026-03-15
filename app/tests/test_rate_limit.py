def test_rate_limit_exceeded(client, test_db):
    api_key = "testkey123"

    for i in range(101):
        response = client.get("/api-keys/", headers={"X-API-Key": api_key})
        if i < 100:
            assert response.status_code == 200
        else:
            assert response.status_code == 429
            assert response.json()["detail"] == "Rate limit exceeded"