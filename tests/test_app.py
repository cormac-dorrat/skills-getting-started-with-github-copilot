from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_read_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities


def test_signup_for_activity():
    # Test successful signup
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up test@mergington.edu for Chess Club"

    # Test signing up again (should fail)
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

    # Test signing up for non-existent activity
    response = client.post("/activities/Non Existent Club/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_unregister_from_activity():
    # First sign up a test user
    email = "testunregister@mergington.edu"
    activity = "Chess Club"
    client.post(f"/activities/{activity}/signup?email={email}")

    # Test successful unregister
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity}"

    # Test unregistering again (should fail)
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

    # Test unregistering from non-existent activity
    response = client.post("/activities/Non Existent Club/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_activity_capacity():
    activity = "Chess Club"
    base_email = "capacity_test{}@mergington.edu"
    
    # Get current participants
    response = client.get("/activities")
    current_participants = len(response.json()[activity]["participants"])
    max_participants = response.json()[activity]["max_participants"]
    
    # Fill up remaining spots
    for i in range(current_participants, max_participants):
        email = base_email.format(i)
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
    
    # Try to register one more (should fail)
    response = client.post(f"/activities/{activity}/signup?email={base_email.format('overflow')}")
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()