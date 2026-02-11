"""
Tests for the FastAPI activities application
"""

import pytest


class TestGetActivities:
    """Test the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that get_activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball" in data
        assert "Tennis Club" in data
        assert "Chess Club" in data

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data

    def test_activity_participants_is_list(self, client):
        """Test that participants field is a list"""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Basketball/signup?email={email}")
        
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Basketball"]["participants"]

    def test_signup_for_nonexistent_activity(self, client):
        """Test that signup fails for nonexistent activity"""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_duplicate_signup_fails(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        email = "james@mergington.edu"
        response = client.post(f"/activities/Basketball/signup?email={email}")
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_accepts_multiple_students(self, client):
        """Test that multiple students can sign up for the same activity"""
        emails = ["student1@mergington.edu", "student2@mergington.edu"]
        
        for email in emails:
            response = client.post(f"/activities/Basketball/signup?email={email}")
            assert response.status_code == 200
        
        response = client.get("/activities")
        participants = response.json()["Basketball"]["participants"]
        for email in emails:
            assert email in participants


class TestUnregisterFromActivity:
    """Test the DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_success(self, client):
        """Test successful unregistration"""
        email = "james@mergington.edu"
        response = client.delete(
            f"/activities/Basketball/signup?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        email = "james@mergington.edu"
        client.delete(f"/activities/Basketball/signup?email={email}")
        
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Basketball"]["participants"]

    def test_unregister_nonexistent_activity(self, client):
        """Test that unregister fails for nonexistent activity"""
        response = client.delete(
            "/activities/NonexistentActivity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_not_registered_student(self, client):
        """Test that unregister fails if student is not registered"""
        response = client.delete(
            "/activities/Basketball/signup?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_then_signup_again(self, client):
        """Test that a student can sign up again after unregistering"""
        email = "james@mergington.edu"
        
        # Unregister
        client.delete(f"/activities/Basketball/signup?email={email}")
        
        # Signup again
        response = client.post(f"/activities/Basketball/signup?email={email}")
        assert response.status_code == 200
        
        # Verify participant is back
        response = client.get("/activities")
        assert email in response.json()["Basketball"]["participants"]


class TestRootEndpoint:
    """Test the root endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
