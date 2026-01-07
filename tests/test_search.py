from fastapi.testclient import TestClient


def test_search_patients(client: TestClient):
    # 1. Create a patient
    client.post(
        "/api/v1/patients/",
        json={
            "first_name": "Find",
            "last_name": "Me",
            "date_of_birth": "1990-01-01",
            "gender": "Male",
        },
    )

    # 2. Create another similar patient (Partial match)
    client.post(
        "/api/v1/patients/",
        json={
            "first_name": "Dont",
            "last_name": "Me",
            "date_of_birth": "1990-01-01",
            "gender": "Female",
        },
    )

    # Test Strategy 1: Full Duplicate Search
    response = client.get(
        "/api/v1/patients/",
        params={
            "first_name": "Find",
            "last_name": "Me",
            "date_of_birth": "1990-01-01",
            "gender": "Male",
        },
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["first_name"] == "Find"

    # Test Strategy 2: Potential Duplicate (Last Name only)
    response = client.get("/api/v1/patients/", params={"last_name": "Me"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2  # Should find both

    # Test Strategy 3: No Match
    response = client.get("/api/v1/patients/", params={"first_name": "Ghost"})
    assert len(response.json()) == 0
    assert len(response.json()) == 0


def test_search_interactions(client: TestClient):
    # Setup: Create 2 Patients
    p1 = client.post(
        "/api/v1/patients/",
        json={
            "first_name": "Interact",
            "last_name": "One",
            "date_of_birth": "2000-01-01",
            "gender": "Male",
        },
    ).json()["id"]

    p2 = client.post(
        "/api/v1/patients/",
        json={
            "first_name": "Interact",
            "last_name": "Two",
            "date_of_birth": "2000-01-01",
            "gender": "Female",
        },
    ).json()["id"]

    client.post(
        "/api/v1/interactions/",
        json={"patient_id": p1, "outcome": "Healthy", "notes": "1"},
    )
    client.post(
        "/api/v1/interactions/",
        json={"patient_id": p1, "outcome": "Critical", "notes": "2"},
    )
    client.post(
        "/api/v1/interactions/",
        json={"patient_id": p2, "outcome": "Healthy", "notes": "3"},
    )

    # 1. Search All
    resp = client.get("/api/v1/interactions/")
    assert resp.status_code == 200
    assert len(resp.json()) >= 3

    # 2. Filter by Patient P1
    resp = client.get(f"/api/v1/interactions/?patient_id={p1}")
    data = resp.json()
    assert len(data) == 2
    assert all(i["patient_id"] == p1 for i in data)

    # 3. Filter by Outcome 'Critical'
    resp = client.get("/api/v1/interactions/?outcome=Critical")
    data = resp.json()
    assert len(data) >= 1
    assert all(i["outcome"] == "Critical" for i in data)

    # 4. Filter by Patient P1 AND Outcome 'Critical'
    resp = client.get(f"/api/v1/interactions/?patient_id={p1}&outcome=Critical")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["patient_id"] == p1
    assert data[0]["outcome"] == "Critical"

    # 5. Filter No Match
    resp = client.get(f"/api/v1/interactions/?patient_id={p2}&outcome=Critical")
    assert len(resp.json()) == 0
