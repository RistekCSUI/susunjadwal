import random
import string
from typing import List


class TestBase:
    @classmethod
    def get_random_string(cls, length):
        letters = string.ascii_letters
        return "".join(random.choice(letters) for _ in range(length))

    @classmethod
    def assert_serialization_contains_keys(
        cls, keys: List[str], serialized_object: dict
    ):
        for k in keys:
            assert k in serialized_object.keys()
