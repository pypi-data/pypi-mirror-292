from django.test import TestCase

from ..choices import DataClass
from .testing_data_class import TestDataClass


class DataClassKeysTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_number_of_choices(self):
        self.assertEqual(len(DataClass), len(TestDataClass))

    def test_choice_key_mapping(self):
        for test_data_enum in TestDataClass:
            data_enum = DataClass.from_key(test_data_enum.CLASS_KEY)
            self.assertEqual(data_enum.CLASS_KEY, test_data_enum.CLASS_KEY)
            self.assertEqual(data_enum.CLASS, test_data_enum.CLASS)
