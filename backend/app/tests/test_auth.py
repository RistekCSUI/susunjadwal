import pytest
from .utils import BASE_PATH, SERVICE_URL, get_ticket_from_sso_ui


@pytest.mark.usefixtures("mongo")
class TestAuth:
    """Test authentication endpoint"""

    @classmethod
    def setup_class(cls):
        cls.path = BASE_PATH + "/auth/"

    def test_auth(self, client):
        ticket = get_ticket_from_sso_ui()
        service_url = SERVICE_URL
        assert ticket is not None

        res = client.post(
            self.path, json={"ticket": ticket, "service_url": service_url}
        )
        assert res.status_code == 200

        res_data = res.get_json()
        assert res_data["token"] is not None
        assert res_data["major_id"] is not None
        assert res_data["user_id"] is not None

    def test_request_with_invalid_auth_should_return_400(self, client):
        request_body = {"tiket": "invalid_ticket", "service_url": "invalid_service_url"}

        response = client.post(self.path, json=request_body)

        assert response.status_code == 400
        assert response.get_json() == {}

    def test_request_without_request_body_should_return_400(self, client):
        response = client.post(self.path, json={})

        assert response.status_code == 400
        assert response.get_json() == {}
