import datetime

import pytest
from mongoengine import ValidationError

from models.major import Major
from models.user import User
from models.user_schedule import ScheduleItem, UserSchedule
from .test_utils import TestBase


@pytest.mark.usefixtures("mongo")
class TestScheduleItem(TestBase):
    def test_serialization_contains_required_keys(self):
        schedule_item = ScheduleItem(
            name="Random",
            day="Monday",
            start="Start",
            end="End",
            room="Canteen",
        )

        serialized_schedule_item = schedule_item.serialize()

        self.assert_serialization_contains_keys(
            keys=["name", "day", "start", "end", "room"],
            serialized_object=serialized_schedule_item,
        )

    def test_serialization_values(self):
        schedule_item = ScheduleItem(
            name="New Name",
            day="Monday",
            start="Start",
            end="End",
            room="Canteen",
        )

        serialized_schedule_item = schedule_item.serialize()

        assert serialized_schedule_item["name"] == schedule_item.name
        assert serialized_schedule_item["day"] == schedule_item.day
        assert serialized_schedule_item["start"] == schedule_item.start
        assert serialized_schedule_item["end"] == schedule_item.end
        assert serialized_schedule_item["room"] == schedule_item.room

    def test_schedule_item_fields_validation(self):
        test_cases = [
            {
                "name": "Name" * 40,
                "day": "Monday" * 10,
                "start": "Start",
                "end": "End",
                "room": "Room",
            },
            {
                "name": "Name" * 40,
                "day": "Monday" * 10,
                "start": "Start" * 5,
                "end": "End",
                "room": "Room",
            },
            {
                "name": "Name" * 40,
                "day": "Monday" * 10,
                "start": "Start" * 5,
                "end": "End" * 10,
                "room": "Room",
            },
            {
                "name": "Name" * 40,
                "day": "Monday" * 10,
                "start": "Start" * 5,
                "end": "End" * 10,
                "room": "Room" * 20,
            },
        ]

        for case in test_cases:
            with pytest.raises(ValidationError):
                ScheduleItem(
                    name=case["name"],
                    day=case["day"],
                    start=case["start"],
                    end=case["end"],
                    room=case["room"],
                ).validate()


@pytest.mark.usefixtures("mongo")
class TestUserSchedule(TestBase):
    @classmethod
    def generate_random_user_item(cls):
        return User(
            name=cls.get_random_string(255),
            username=cls.get_random_string(64),
            npm=cls.get_random_string(20),
            batch=cls.get_random_string(5),
            major=Major.objects().create(
                name=cls.get_random_string(256),
                kd_org=cls.get_random_string(16),
            ),
        )

    @classmethod
    def generate_random_schedule_item(cls):
        return ScheduleItem(
            name=cls.get_random_string(128),
            day=cls.get_random_string(16),
            room=cls.get_random_string(64),
            start=cls.get_random_string(16),
            end=cls.get_random_string(16),
        )

    def test_add_schedule_item_should_increase_the_schedule_item(self):
        user_schedule = UserSchedule(
            user_id=self.generate_random_user_item(), name="User Schedule A"
        )
        assert len(user_schedule.schedule_items) == 0

        inserted_schedule = user_schedule.add_schedule_item(
            name="Schedule A", day="Day A", room="Room A", start="Start", end="End"
        )

        assert len(user_schedule.schedule_items) == 1
        assert inserted_schedule.name == "Schedule A"
        assert inserted_schedule.day == "Day A"
        assert inserted_schedule.room == "Room A"
        assert inserted_schedule.start == "Start"
        assert inserted_schedule.end == "End"

    def test_user_schedule_creation(self):
        created_datetime = datetime.datetime(
            year=2020, month=12, day=2, hour=8, minute=30
        )
        user = self.generate_random_user_item().save()
        schedule_item = self.generate_random_schedule_item()
        user_schedule = UserSchedule.objects().create(
            user_id=user,
            name="Dummy Schedule",
            deleted=False,
            schedule_items=[schedule_item],
            created_at=created_datetime,
        )

        user_schedules = UserSchedule.objects
        assert len(user_schedules) == 1
        assert user_schedule in user_schedules

        fetched_user_schedule = user_schedules().first()
        assert fetched_user_schedule.user_id == user
        assert fetched_user_schedule.name == "Dummy Schedule"
        assert not fetched_user_schedule.deleted
        assert len(fetched_user_schedule.schedule_items) == 1
        assert schedule_item in fetched_user_schedule.schedule_items
        assert fetched_user_schedule.created_at == created_datetime

        user_schedule.delete()

    def test_user_schedule_update(self):
        user_schedule = UserSchedule.objects().create(
            user_id=None, name="Old Schedule", schedule_items=[]
        )

        new_user = self.generate_random_user_item().save()
        new_schedule_item = self.generate_random_schedule_item()
        new_created_at = datetime.datetime(year=2020, month=12, day=3, hour=8)
        user_schedule.user_id = new_user
        user_schedule.name = "New Schedule"
        user_schedule.schedule_items = [new_schedule_item]
        user_schedule.deleted = True
        user_schedule.created_at = new_created_at
        user_schedule.save()
        user_schedule.reload()

        assert user_schedule.user_id == new_user
        assert user_schedule.name == "New Schedule"
        assert new_schedule_item in user_schedule.schedule_items
        assert user_schedule.deleted
        assert user_schedule.created_at == new_created_at

        user_schedule.delete()

    def test_user_schedule_deletion(self):
        user_schedule = UserSchedule.objects().create(
            user_id=self.generate_random_user_item().save(),
            name=self.get_random_string(128),
            schedule_items=[],
        )

        assert len(UserSchedule.objects) == 1
        assert user_schedule in UserSchedule.objects

        user_schedule.delete()
        assert len(UserSchedule.objects) == 0
        assert user_schedule not in UserSchedule.objects

    def test_serialization_contains_required_keys(self):
        user_schedule = UserSchedule(
            user_id=self.generate_random_user_item(), name="User Schedule B"
        )

        serialized_user_schedule = user_schedule.serialize()

        self.assert_serialization_contains_keys(
            keys=["id", "name", "created_at", "schedule_items"],
            serialized_object=serialized_user_schedule,
        )

    def test_serialize_with_empty_schedule_items(self):
        user_schedule = UserSchedule(
            user_id=self.generate_random_user_item(), name="User Schedule C"
        )

        serialized_user_schedule = user_schedule.serialize()

        assert serialized_user_schedule["name"] == user_schedule.name
        assert serialized_user_schedule["schedule_items"] == []

    def test_serialize_with_schedule_items(self):
        schedule_item = self.generate_random_schedule_item()
        user_schedule = UserSchedule(
            user_id=self.generate_random_user_item(),
            name="User Schedule A",
            schedule_items=[schedule_item],
        )

        serialized_user_schedule = user_schedule.serialize()

        assert serialized_user_schedule["name"] == user_schedule.name
        assert len(serialized_user_schedule["schedule_items"]) == 1
        assert (
            serialized_user_schedule["schedule_items"][0] == schedule_item.serialize()
        )

    def test_user_schedule_fields_validation(self):
        schedule_item = self.generate_random_schedule_item()
        user = self.generate_random_user_item()
        now = datetime.datetime.now()
        test_cases = [
            {
                "user_id": schedule_item,
                "name": "Name",
                "schedule_items": [schedule_item],
                "created_at": now,
            },
            {
                "user_id": schedule_item,
                "name": "Name" * 40,
                "schedule_items": [schedule_item],
                "created_at": now,
            },
            {
                "user_id": schedule_item,
                "name": "Name" * 40,
                "schedule_items": user,
                "created_at": now,
            },
            {
                "user_id": schedule_item,
                "name": "Name" * 40,
                "schedule_items": user,
                "created_at": "Now",
            },
        ]

        for case in test_cases:
            with pytest.raises(ValidationError):
                UserSchedule(
                    user_id=case["user_id"],
                    name=case["name"],
                    schedule_items=case["schedule_items"],
                    created_at=case["created_at"],
                ).validate()
