"""
Test UI activation flow using a context manager approach for session mocking.
This provides more control and is reusable across different tests.
"""

from uuid import uuid4

from src.tests.helpers import mock_session, random_user


def test_complete_ui_activation_flow_with_context_manager(client):
    """
    Test the complete user lifecycle using the context manager approach.
    """
    # 1. Create a user using REST API route
    user_data = random_user()
    user_response = client.post("/users/", json=user_data)
    assert user_response.status_code == 201
    created_user = user_response.json()
    assert created_user["email"] == user_data["email"]
    assert created_user["is_verified"] is False

    # 2. Verify that groups/search does not work as the user is not yet verified
    search_response_unverified = client.get(
        "/groups/search", params={"user_email": user_data["email"]}
    )
    assert search_response_unverified.status_code == 423  # User not verified

    # 3. Test activation page without session (should show activation page)
    activation_page_response = client.get("/ui/activation")
    assert activation_page_response.status_code == 200

    # 4. Simulate ProConnect callback session and activate user
    user_sub = uuid4()
    session_data = {
        "user_email": user_data["email"],
        "user_sub": str(user_sub),
        "is_super_admin": False,
    }

    with mock_session(session_data):
        # Test redirect behavior when session exists
        redirect_response = client.get("/ui/activation", follow_redirects=False)
        assert redirect_response.status_code == 302
        assert redirect_response.headers["location"] == "/ui/activation/succes"

        # Activate the user via UI success page
        activation_success_response = client.get("/ui/activation/succes")
        assert activation_success_response.status_code == 200

    # 5. Verify that groups/search now works for the activated user
    search_response_verified = client.get(
        "/groups/search",
        params={"user_email": user_data["email"], "user_sub": str(user_sub)},
    )
    assert search_response_verified.status_code == 200
    groups = search_response_verified.json()
    assert isinstance(groups, list)
    assert len(groups) == 0

    # Additional verification: check that user is now verified
    user_check_response = client.get(
        "/users/search", params={"email": user_data["email"]}
    )
    assert user_check_response.status_code == 200
    verified_user = user_check_response.json()
    assert verified_user["is_verified"] is True


def test_multiple_session_scenarios_with_context_manager(client):
    """
    Test various session scenarios using the context manager.
    """
    user_data = random_user()
    client.post("/users/", json=user_data)
    user_sub = uuid4()

    # Test with empty session
    with mock_session({}):
        response = client.get("/ui/activation/succes")
        assert response.status_code == 403  # Forbidden due to missing session data

    # Test with incomplete session (missing user_sub)
    with mock_session({"user_email": user_data["email"]}):
        response = client.get("/ui/activation/succes")
        assert response.status_code == 403  # Forbidden due to missing user_sub

    # Test with complete session
    complete_session = {
        "user_email": user_data["email"],
        "user_sub": str(user_sub),
        "is_super_admin": False,
    }
    with mock_session(complete_session):
        response = client.get("/ui/activation/succes")
        assert response.status_code == 200  # Should succeed
