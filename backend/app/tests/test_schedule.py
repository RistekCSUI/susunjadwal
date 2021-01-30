from models.user_schedule import UserSchedule
from .utils import BASE_PATH


class TestSchedule:
    """Test user schedule related endpoint
    This test class use auth_client fixture. See conftest.py for more info."""

    schedule_items = [
        {
            "day": "Senin",
            "end": "09.40",
            "room": "A6.09 (Ged Baru)",
            "start": "08.00",
            "name": "Anum - A"
        },
        {
            "day": "Rabu",
            "end": "08.50",
            "room": "A6.09 (Ged Baru)",
            "start": "08.00",
            "name": "Anum - A"
        },
        {
            "day": "Selasa",
            "end": "09.40",
            "room": "2.2304",
            "start": "08.00",
            "name": "Basis Data - A"
        },
        {
            "day": "Kamis",
            "end": "09.40",
            "room": "2.2404",
            "start": "08.00",
            "name": "Basis Data - A"
        },
    ]

    def test_get_empty_user_schedules(self, auth_client):
        client, user = auth_client
        url = '{}/users/{}/user_schedules'.format(BASE_PATH, user.id)
        res = client.get(url)

        assert res.status_code == 200
        assert res.get_json()['user_schedules'] == []

        user_schedules = UserSchedule.objects(user_id=user.id).all()
        assert len(user_schedules) == 0

    def test_save_user_schedule(self, auth_client):
        client, user = auth_client
        url = '{}/users/{}/user_schedule'.format(BASE_PATH, user.id)
        res = client.post(url, json={
            'schedule_items': self.schedule_items})

        assert res.status_code == 201
        assert res.get_json()['id']

        user_schedules = UserSchedule.objects(user_id=user.id).all()
        assert len(user_schedules) == 1

    def create_user_schedule(self, user):
        """Create user schedule directly from db"""
        user_schedule = UserSchedule(user_id=user.id)
        for item in self.schedule_items:
            user_schedule.add_schedule_item(**item)
        user_schedule.save()
        return user_schedule

    def test_get_saved_user_schedule_list(self, auth_client):
        client, user = auth_client
        user_schedule = self.create_user_schedule(user)

        url = '{}/users/{}/user_schedules'.format(BASE_PATH, user.id)
        res = client.get(url)

        assert res.status_code == 200
        res_json = res.get_json()['user_schedules']
        assert len(res_json) == 1
        assert res_json[0]['id'] == str(user_schedule.id)
        assert res_json[0]['schedule_items'] == self.schedule_items

    def test_get_saved_user_schedule_detail(self, auth_client):
        client, user = auth_client
        user_schedule = self.create_user_schedule(user)

        url = '{}/user_schedules/{}'.format(BASE_PATH, user_schedule.id)
        res = client.get(url)

        assert res.status_code == 200
        res_json = res.get_json()['user_schedule']
        assert res_json['id'] == str(user_schedule.id)
        assert res_json['created_at']
        assert res_json['has_edit_access'] is True
        assert res_json['name'] is None
        assert res_json['schedule_items'] == self.schedule_items

    def test_rename_user_schedule(self, auth_client):
        client, user = auth_client
        user_schedule = self.create_user_schedule(user)

        url = '{}/users/{}/user_schedules/{}/change_name'.format(
            BASE_PATH, user.id, user_schedule.id)
        SCHEDULE_NAME = 'Testing Schedule'
        res = client.post(url, json={'name': SCHEDULE_NAME})

        assert res.status_code == 200
        res_json = res.get_json()['user_schedule']
        assert res_json['created_at']
        assert res_json['id'] == str(user_schedule.id)
        assert res_json['name'] == SCHEDULE_NAME
        assert res_json['schedule_items'] == self.schedule_items

        user_schedule.reload()
        assert user_schedule.name == SCHEDULE_NAME

    def test_delete_user_schedule(self, auth_client):
        client, user = auth_client
        user_schedule = self.create_user_schedule(user)

        url = '{}/users/{}/user_schedules/{}'.format(
            BASE_PATH, user.id, user_schedule.id)
        res = client.delete(url)

        assert res.status_code == 204

        user_schedule.reload()
        assert user_schedule.deleted
