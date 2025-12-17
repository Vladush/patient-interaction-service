import uuid
from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session


# Helper to create a patient
def create_patient(client: TestClient) -> str:
    response = client.post(
        "/api/v1/patients/",
        json={"first_name": "John", "last_name": "Doe", "date_of_birth": "1980-01-01", "gender": "Male"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_interaction(client: TestClient):
    patient_id = create_patient(client)

    response = client.post(
        "/api/v1/interactions/",
        json={
            "patient_id": patient_id,
            "outcome": "Healthy",
            "notes": "Regular checkup.",
        },
    )
    data = response.json()
    assert response.status_code == 201
    assert data["outcome"] == "Healthy"
    assert data["patient_id"] == patient_id
    assert "id" in data
    assert "timestamp" in data


def test_create_interaction_patient_not_found(client: TestClient):
    random_id = str(uuid.uuid4())
    response = client.post(
        "/api/v1/interactions/",
        json={
            "patient_id": random_id,
            "outcome": "Monitor",
            "notes": "This should fail.",
        },
    )
    assert response.status_code == 404


def test_read_patient_history(client: TestClient):
    patient_id = create_patient(client)

    # Create two interactions
    client.post(
        "/api/v1/interactions/",
        json={"patient_id": patient_id, "outcome": "Healthy", "notes": "First"},
    )

    client.post(
        "/api/v1/interactions/",
        json={"patient_id": patient_id, "outcome": "Critical", "notes": "Second"},
    )



    response = client.get(f"/api/v1/interactions/?patient_id={patient_id}")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    # Verify ordering: newest first
    assert data[0]["outcome"] == "Critical"
    assert data[1]["outcome"] == "Healthy"


def test_read_history_patient_not_found(client: TestClient):
    random_id = str(uuid.uuid4())
    # Search behavior: returns empty list, not 404
    response = client.get(f"/api/v1/interactions/?patient_id={random_id}")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_delete_patient(client: TestClient):
    patient_id = create_patient(client)
    
    # Create an interaction to ensure it gets deleted
    client.post(
        "/api/v1/interactions/",
        json={"patient_id": patient_id, "outcome": "Healthy", "notes": "To be deleted"},
    )
    
    # Delete Patient
    response = client.delete(f"/api/v1/patients/{patient_id}")
    assert response.status_code == 204
    
    # Verify Patient Gone
    # Best proxy: Check history returns empty list (Patient not found logic removed)
    response = client.get(f"/api/v1/interactions/?patient_id={patient_id}")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_delete_interaction(client: TestClient):
    patient_id = create_patient(client)
    
    # Create an interaction
    response = client.post(
        "/api/v1/interactions/",
        json={"patient_id": patient_id, "outcome": "Healthy", "notes": "To be deleted"},
    )
    interaction_id = response.json()["id"]
    
    # Delete Interaction
    response = client.delete(f"/api/v1/interactions/{interaction_id}")
    assert response.status_code == 204
    
    # Verify Interaction Gone from History
    response = client.get(f"/api/v1/interactions/?patient_id={patient_id}")
    data = response.json()
    assert len(data) == 0
    
    # Verify Patient Still Exists (optional, but good sanity check)
    # Trying to create another interaction should succeed
    response = client.post(
        "/api/v1/interactions/",
        json={"patient_id": patient_id, "outcome": "Monitor", "notes": "New one"},
    )
    assert response.status_code == 201


def test_configurable_outcomes(client: TestClient):
    patient_id = create_patient(client)

    # Try to use "Recovered" (Not yet configured) -> Should Fail
    response = client.post(
        "/api/v1/interactions/",
        json={"patient_id": patient_id, "outcome": "Recovered", "notes": "New"},
    )
    assert response.status_code == 400
    
    # Configure "Recovered"
    response = client.post("/api/v1/outcomes/", json={"code": "Recovered"})
    assert response.status_code == 201
    
    # Try "Recovered" again -> Should Success
    response = client.post(
        "/api/v1/interactions/",
        json={"patient_id": patient_id, "outcome": "Recovered", "notes": "New"},
    )
    assert response.status_code == 201
    
    # Verify History is Intact after Deletion
    client.delete("/api/v1/outcomes/Recovered")
    
    history = client.get(f"/api/v1/interactions/?patient_id={patient_id}")
    data = history.json()
    assert len(data) > 0
    assert data[0]["outcome"] == "Recovered"


def test_update_patient(client: TestClient):
    patient_id = create_patient(client)
    
    # Update Name
    response = client.put(
        f"/api/v1/patients/{patient_id}",
        json={"first_name": "Jane", "last_name": "Smith"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Smith"
    assert data["gender"] == "Male"  # Should remain unchanged


def test_update_interaction(client: TestClient):
    patient_id = create_patient(client)
    
    # Create Interaction
    response = client.post(
        "/api/v1/interactions/",
        json={"patient_id": patient_id, "outcome": "Healthy", "notes": "Original"},
    )
    interaction_id = response.json()["id"]
    
    # Update Notes and Outcome
    response = client.put(
        f"/api/v1/interactions/{interaction_id}",
        json={"outcome": "Critical", "notes": "Updated Note"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["outcome"] == "Critical"
    assert data["notes"] == "Updated Note"


def test_update_outcome(client: TestClient):
    # Create Outcome
    code = "CustomStatus"
    client.post("/api/v1/outcomes/", json={"code": code, "description": "Original Desc"})
    
    # Update Description
    response = client.put(
        f"/api/v1/outcomes/{code}",
        json={"code": code, "description": "Updated Desc"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated Desc"
    # Ensure code wasn't changed
    assert data["code"] == code
