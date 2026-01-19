import pytest
from src.app import activities


def test_root_redirect(client):
    response = client.get("/")
    assert response.status_code == 200
    assert str(response.url).endswith("/static/index.html")


def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data
    assert "description" in data["Basketball Team"]
    assert "schedule" in data["Basketball Team"]
    assert "max_participants" in data["Basketball Team"]
    assert "participants" in data["Basketball Team"]


def test_signup_success(client):
    # Test successful signup
    initial_participants = activities["Basketball Team"]["participants"].copy()
    response = client.post("/activities/Basketball%20Team/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up newstudent@mergington.edu for Basketball Team" in data["message"]
    # Check that participant was added
    assert "newstudent@mergington.edu" in activities["Basketball Team"]["participants"]
    # Clean up
    activities["Basketball Team"]["participants"] = initial_participants


def test_signup_activity_not_found(client):
    response = client.post("/activities/NonExistent%20Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Activity not found"


def test_signup_already_signed_up(client):
    # First signup
    response = client.post("/activities/Basketball%20Team/signup?email=duplicate@mergington.edu")
    assert response.status_code == 200
    # Try to signup again
    response = client.post("/activities/Basketball%20Team/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Student already signed up for this activity"
    # Clean up
    activities["Basketball Team"]["participants"].remove("duplicate@mergington.edu")


def test_unregister_success(client):
    # First signup
    client.post("/activities/Basketball%20Team/signup?email=temp@mergington.edu")
    # Then unregister
    response = client.delete("/activities/Basketball%20Team/unregister?email=temp@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered temp@mergington.edu from Basketball Team" in data["message"]
    # Check that participant was removed
    assert "temp@mergington.edu" not in activities["Basketball Team"]["participants"]


def test_unregister_activity_not_found(client):
    response = client.delete("/activities/NonExistent%20Activity/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Activity not found"


def test_unregister_not_signed_up(client):
    response = client.delete("/activities/Basketball%20Team/unregister?email=notsignedup@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Student not signed up for this activity"