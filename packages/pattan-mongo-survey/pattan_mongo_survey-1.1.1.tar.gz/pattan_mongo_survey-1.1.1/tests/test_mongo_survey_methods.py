import unittest
from src.pattan_mongo_survey.mongo import MongoSurveyService
import src.pattan_mongo_survey.exceptions as exceptions
from unittest.mock import patch


class TestStringMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        configuration_object = {
            'MONGDB_USER': 'user',
            'MONGDB_PASSWD': 'password',
            'MONGDB_HOST': 'localhost',
            'MONGDB_DB': 'database',
            'MONGDB_SURVEY_COLLECTION': 'survey_collection',
            'MONGDB_DB_RESPONSE_COLLECTION': 'response_collection',
        }
        with patch.object(MongoSurveyService, "__init__", lambda configuration_object: None):
            cls.mss = MongoSurveyService()

    def test_get_connection_string_exists(self):
        exists = getattr(self.mss, "_get_mongo_connection_string", None)
        is_callable = None
        if exists:
            is_callable = callable(exists)
        self.assertTrue(is_callable)

    def test_get_survey_list_exists(self):
        exists = getattr(self.mss, "get_survey_list", None)
        is_callable = None
        if exists:
            is_callable = callable(exists)
        self.assertTrue(is_callable)

    def test_get_survey_requires_survey_id(self):
        self.assertRaises(exceptions.MissingSurveyId, self.mss.get_survey)

    def test_save_survey_response_requires_response(self):
        self.assertRaises(exceptions.DataSaveFailure, self.mss.save_survey_response)

    def test_save_survey_response_requires_survey_id(self):
        self.assertRaises(exceptions.MissingSurveyId, self.mss.save_survey_response, 'response')

    def test_save_survey_exists(self):
        exists = getattr(self.mss, "save_survey", None)
        is_callable = None
        if exists:
            is_callable = callable(exists)
        self.assertTrue(is_callable)

    def test_get_survey_responses_requires_survey_id(self):
        self.assertRaises(exceptions.MissingSurveyId, self.mss.get_survey_responses )

    def test_delete_survey_responses_requires_survey_id(self):
        self.assertRaises(exceptions.MissingSurveyId, self.mss.delete_survey_responses )