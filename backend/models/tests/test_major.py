import pytest
from mongoengine import ValidationError

from models.major import Major
from .test_utils import TestBase


@pytest.mark.usefixtures("mongo")
class TestMajor(TestBase):
    def test_major_creation(self):
        major = Major.objects().create(name="Test_Name", kd_org="Test_KD_ORG")

        majors = Major.objects
        assert len(majors) == 1
        assert major in majors

        fetched_major = majors().first()
        assert fetched_major.name == "Test_Name"
        assert fetched_major.kd_org == "Test_KD_ORG"

        major.delete()

    def test_major_update(self):
        major = Major.objects.create(name="Old_Name", kd_org="Old_KD_ORG")

        major.name = "Updated_Name"
        major.kd_org = "Updated_KD_ORG"
        major.save()
        major.reload()

        assert major.name == "Updated_Name"
        assert major.kd_org == "Updated_KD_ORG"

        major.delete()

    def test_major_deletion(self):
        major = Major.objects().create(name="Test_Name", kd_org="Test_KD_ORG")

        assert len(Major.objects) == 1
        assert major in Major.objects

        major.delete()
        assert len(Major.objects) == 0
        assert major not in Major.objects

    def test_major_fields_with_invalid_values(self):
        field_values = [
            {"name": "A" * 257, "kd_org": ""},
            {"name": "A" * 257, "kd_org": "KD_ORG"},
            {"name": "A" * 257, "kd_org": "B" * 17},
            {"name": "A" * 257, "kd_org": "B" * 20},
            {"name": "A" * 300, "kd_org": ""},
            {"name": "A" * 300, "kd_org": "KD_ORG"},
            {"name": "A" * 300, "kd_org": "B" * 17},
            {"name": "A" * 300, "kd_org": "B" * 20},
        ]

        for values in field_values:
            with pytest.raises(ValidationError):
                Major(name=values["name"], kd_org=values["kd_org"]).validate()
