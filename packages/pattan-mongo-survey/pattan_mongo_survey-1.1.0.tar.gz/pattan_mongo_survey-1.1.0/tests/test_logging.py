import unittest
from src.pattan_mongo_survey.mongo import MongoSurveyService
from unittest.mock import patch, Mock


class TestStringMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.configuration_object = {
            'MONGDB_USER': 'user',
            'MONGDB_PASSWD': 'password',
            'MONGDB_HOST': 'localhost',
            'MONGDB_DB': 'database',
            'MONGDB_SURVEY_COLLECTION': 'survey_collection',
            'MONGDB_DB_RESPONSE_COLLECTION': 'response_collection',
        }
        cls.config = cls.configuration_object.copy()
        # to is to mock the constructor so we can get an object instance and still call methods for testing
        with patch.object(MongoSurveyService, "__init__", lambda configuration_object: None):
            cls.mss = MongoSurveyService()

    def test_constructor_logs_missing_configuration_error(self):
        with self.assertLogs('pattan_mongo_survey', level='DEBUG') as cm:
            try:
                mss = MongoSurveyService()
            except Exception as e:
                pass
        self.assertEqual(cm.output, ['CRITICAL:pattan_mongo_survey:Missing configuration dictionary'])

    def test_constructor_logs_missing_configuration_key_error(self):
        with self.assertLogs('pattan_mongo_survey', level='DEBUG') as cm:
            del self.config['MONGDB_USER']
            try:
                MongoSurveyService(self.config)
            except Exception as e:
                pass
        self.assertEqual(cm.output, ['CRITICAL:pattan_mongo_survey:Missing configuration dictionary keys: MONGDB_USER'])

    def test_constructor_logs_configuration_object_validation_passes(self):
        with self.assertLogs('pattan_mongo_survey', level='DEBUG') as cm:
            try:
                MongoSurveyService(self.configuration_object)
            except Exception as e:
                pass
        self.assertEqual(cm.output, ['DEBUG:pattan_mongo_survey:configuration object passes'])
