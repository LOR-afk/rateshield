def test_health(client):
    assert client.get("/api/health").json()["status"] == "ok"


def test_rate_limit(client):
    response = client.put("/api/policy", json={"max_requests": 2, "window_seconds": 60, "failed_login_threshold": 3})
    assert response.status_code == 200
    assert client.get("/api/protected/ping").status_code == 200
    assert client.get("/api/protected/ping").status_code == 200
    blocked = client.get("/api/protected/ping")
    assert blocked.status_code == 429
    assert "Retry-After" in blocked.headers
    assert client.get("/api/summary").json()["blocked_requests"] == 1


def test_failed_logins(client):
    client.put("/api/policy", json={"max_requests": 5, "window_seconds": 60, "failed_login_threshold": 2})
    assert client.post("/api/demo/login", json={"success": False}).json()["suspicious"] is False
    assert client.post("/api/demo/login", json={"success": False}).json()["suspicious"] is True
    assert client.get("/api/summary").json()["login_failures"] == 2


def test_policy_validation(client):
    assert client.put("/api/policy", json={"max_requests": 0, "window_seconds": 60, "failed_login_threshold": 2}).status_code == 422


def test_events_are_metadata_only(client):
    client.post("/api/demo/login", json={"success": False})
    events = client.get("/api/events").json()
    assert events[0]["detail"] == "Simulated invalid credentials"
