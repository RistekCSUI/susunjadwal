import pytest
from mongoengine import ValidationError

from models.user import User
from models.major import Major
from .test_utils import TestBase


@pytest.mark.usefixtures("mongo")
class TestUser(TestBase):
    def test_user_creation(self):
        major = Major.objects().create(name="Test_Name", kd_org="Test_KD_ORG")
        User.objects().create(
            name="John", username="wick", npm="12345678", batch="2020", major=major
        )

        users = User.objects
        assert len(users) == 1

        fetched_user = users.first()
        assert fetched_user.name == "John"
        assert fetched_user.username == "wick"
        assert fetched_user.npm == "12345678"
        assert fetched_user.batch == "2020"
        assert fetched_user.major == major

        fetched_user.delete()
        major.delete()

    def test_user_update(self):
        old_major = Major.objects().create(name="Test_Name", kd_org="Test_KD_ORG")
        user = User.objects().create(
            name="John", username="wick", npm="12345678", batch="2020", major=old_major
        )

        user.name = "Smith"
        user.username = "wock"
        user.npm = "0123"
        user.batch = "123"
        new_major = Major.objects().create(name="New_Major", kd_org="New_KD_ORG")
        user.major = new_major
        user.save()
        user.reload()

        assert user.name == "Smith"
        assert user.username == "wock"
        assert user.npm == "0123"
        assert user.batch == "123"
        assert user.major == new_major

        user.delete()
        new_major.delete()
        old_major.delete()

    def test_user_deletion(self):
        user = User.objects().create(
            name="John",
            username="wick",
            npm="12345678",
            batch="2020",
            major=Major.objects().create(name="Test_Name", kd_org="Test_KD_ORG"),
        )

        assert len(User.objects) == 1
        assert user in User.objects

        user.delete()
        assert len(User.objects) == 0
        assert user not in User.objects

    def test_user_fields_validation(self):
        major = Major.objects().create(name="Name", kd_org="KD_ORG")
        test_cases = [
            {
                "name": "A" * 300,
                "username": "username",
                "npm": "123",
                "batch": "123",
                "major": major,
            },
            {
                "name": "A" * 300,
                "username": "A" * 100,
                "npm": "123",
                "batch": "123",
                "major": major,
            },
            {
                "name": "A" * 300,
                "username": "A" * 100,
                "npm": "A" * 30,
                "batch": "123",
                "major": major,
            },
            {
                "name": "A" * 300,
                "username": "A" * 100,
                "npm": "A" * 30,
                "batch": "A" * 10,
                "major": major,
            },
            {
                "name": "A" * 300,
                "username": "A" * 100,
                "npm": "A" * 30,
                "batch": "A" * 10,
                "major": 1,
            },
        ]

        for case in test_cases:
            with pytest.raises(ValidationError):
                User(
                    name=case["name"],
                    username=case["username"],
                    npm=case["npm"],
                    batch=case["batch"],
                    major=case["major"],
                ).validate()
