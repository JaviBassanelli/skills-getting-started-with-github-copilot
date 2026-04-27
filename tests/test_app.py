import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Fixture to reset activities to a known state before each test
@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: Reset activities to initial state
    global activities
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": []
        }
    })

client = TestClient(app)

def test_get_activities():
    # Act: Call the GET /activities endpoint
    response = client.get("/activities")
    
    # Assert: Check status and response
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu"]

def test_signup_successful():
    # Arrange: Ensure the student is not already signed up
    assert "emma@mergington.edu" not in activities["Programming Class"]["participants"]
    
    # Act: Sign up for Programming Class
    response = client.post("/activities/Programming%20Class/signup?email=emma@mergington.edu")
    
    # Assert: Check success and participant added
    assert response.status_code == 200
    data = response.json()
    assert "Signed up emma@mergington.edu for Programming Class" in data["message"]
    assert "emma@mergington.edu" in activities["Programming Class"]["participants"]

def test_signup_duplicate():
    # Arrange: Student already signed up
    activities["Chess Club"]["participants"].append("daniel@mergington.edu")
    
    # Act: Try to sign up again
    response = client.post("/activities/Chess%20Club/signup?email=daniel@mergington.edu")
    
    # Assert: Check error
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up" in data["detail"]

def test_signup_invalid_activity():
    # Act: Try to sign up for non-existent activity
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    
    # Assert: Check 404
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_successful():
    # Arrange: Ensure student is signed up
    activities["Chess Club"]["participants"].append("daniel@mergington.edu")
    
    # Act: Unregister
    response = client.delete("/activities/Chess%20Club/unregister?email=daniel@mergington.edu")
    
    # Assert: Check success and participant removed
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered daniel@mergington.edu from Chess Club" in data["message"]
    assert "daniel@mergington.edu" not in activities["Chess Club"]["participants"]

def test_unregister_not_signed_up():
    # Act: Try to unregister a student not signed up
    response = client.delete("/activities/Programming%20Class/unregister?email=notsigned@mergington.edu")
    
    # Assert: Check error
    assert response.status_code == 400
    data = response.json()
    assert "Student not signed up" in data["detail"]

def test_unregister_invalid_activity():
    # Act: Try to unregister from non-existent activity
    response = client.delete("/activities/NonExistent/unregister?email=test@mergington.edu")
    
    # Assert: Check 404
    data = response.json()
    assert "Activity not found" in data["detail"]