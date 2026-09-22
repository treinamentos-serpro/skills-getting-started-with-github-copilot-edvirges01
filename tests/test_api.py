from src import app as app_module


class TestRootEndpoint:
    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location


class TestActivitiesEndpoint:
    def test_get_activities_returns_the_activity_catalog(self, client):
        # Arrange
        expected_activity = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert response.status_code == 200
        assert len(activities) == 9
        assert expected_activity in activities
        assert activities[expected_activity]["participants"] == [
            "michael@mergington.edu",
            "daniel@mergington.edu",
        ]


class TestSignupEndpoint:
    def test_signup_adds_a_student_to_an_activity(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {email} for {activity_name}"
        }
        assert email in app_module.activities[activity_name]["participants"]

    def test_signup_rejects_a_duplicate_student(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json() == {
            "detail": "Student already signed up for this activity"
        }

    def test_signup_rejects_an_unknown_activity(self, client):
        # Arrange
        activity_name = "Robotics Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}


class TestUnregisterEndpoint:
    def test_unregister_removes_a_student_from_an_activity(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email} from {activity_name}"
        }
        assert email not in app_module.activities[activity_name]["participants"]

    def test_unregister_rejects_a_student_who_is_not_signed_up(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "not.signed.up@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json() == {
            "detail": "Student is not signed up for this activity"
        }

    def test_unregister_rejects_an_unknown_activity(self, client):
        # Arrange
        activity_name = "Robotics Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}

    def test_signup_then_unregister_completes_the_student_lifecycle(self, client):
        # Arrange
        activity_name = "Drama Club"
        email = "student@mergington.edu"

        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )
        unregister_response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert signup_response.status_code == 200
        assert unregister_response.status_code == 200
        assert email not in app_module.activities[activity_name]["participants"]
