from app import app
from models.period import Class, Course, Period, ScheduleItem
from .utils import BASE_PATH


class TestCourse:
    """Test get course list endpoint
    This test class use auth_client fixture. See conftest.py for more info."""

    COURSE = {
        "name": "Analisis Numerik",
        "credit": 3,
        "term": 6,
    }

    def test_get_courses_with_period(self, auth_client):
        client, user = auth_client
        self.create_period(user.major.id, is_detail=True)

        url = "{}/majors/{}/courses".format(BASE_PATH, user.major.id)
        res = client.get(url)

        assert res.status_code == 200
        res_json = res.get_json()
        assert res_json["is_detail"]
        assert res_json["name"] == app.config["ACTIVE_PERIOD"]

        assert len(res_json["courses"]) == 1
        course_data = res_json["courses"][0]
        assert course_data["name"] == self.COURSE["name"]
        assert course_data["credit"] == self.COURSE["credit"]
        assert course_data["term"] == self.COURSE["term"]

        assert len(course_data["classes"]) == 1
        class_data = course_data["classes"][0]
        assert len(class_data["lecturer"]) == 2
        assert len(class_data["schedule_items"]) == 1

    def test_get_courses_without_period(self, auth_client):
        client, user = auth_client
        self.create_period(major_id=user.major.id, is_detail=False)

        url = "{}/majors/{}/courses".format(BASE_PATH, user.major.id)
        res = client.get(url)

        assert res.status_code == 200
        res_json = res.get_json()
        assert not res_json["is_detail"]
        assert res_json["name"] == app.config["ACTIVE_PERIOD"]

    def create_period(self, major_id, is_detail):
        """Create dummy period with its course and class"""

        class_obj = Class(
            name="Anum - A",
            schedule_items=[
                ScheduleItem(
                    day="Senin",
                    start="09.40",
                    end="08.00",
                    room="A6.09 (Ged Baru)",
                ),
            ],
            lecturer=["Nama Dosen 1", "Nama Dosen 2"],
        )

        course = Course(
            name=self.COURSE["name"],
            credit=self.COURSE["credit"],
            term=self.COURSE["term"],
            classes=[class_obj],
        )

        period = Period.objects().create(
            major_id=major_id,
            name=app.config["ACTIVE_PERIOD"],
            is_detail=is_detail,
            courses=[course],
        )

        return period
