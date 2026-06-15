from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    return TestClient(app)


def test_root_redirects_to_static_index(client):
    # Arrange: se usa el client preparado
    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    assert isinstance(response.json(), dict)


def test_signup_adds_new_participant(client):
    # Arrange
    activity_name = "Programming Class"
    new_email = "newstudent@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(signup_url, params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert new_email in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"


def test_signup_duplicate_participant_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(signup_url, params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_nonexistent_activity_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(signup_url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_removes_existing_student(client):
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = "michael@mergington.edu"
    remove_url = f"/activities/{activity_name}/remove"

    # Act
    response = client.post(remove_url, params={"email": email_to_remove})

    # Assert
    assert response.status_code == 200
    assert email_to_remove not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Removed {email_to_remove} from {activity_name}"


def test_remove_missing_participant_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missing@mergington.edu"
    remove_url = f"/activities/{activity_name}/remove"

    # Act
    response = client.post(remove_url, params={"email": missing_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"
