import unittest
from src.pattan_mongo_survey.mongo import MongoSurveyService
import src.pattan_mongo_survey.exceptions as exceptions


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.configuration_object = {
            'MONGDB_USER': 'user',
            'MONGDB_PASSWD': 'password',
            'MONGDB_HOST': 'localhost',
            'MONGDB_DB': 'database',
            'MONGDB_SURVEY_COLLECTION': 'survey_collection',
            'MONGDB_DB_RESPONSE_COLLECTION': 'response_collection',
        }

    def test_missing_configuration_object_raises_exception(self):
        self.assertRaises(exceptions.PattanMongoSurveyConfigurationError, MongoSurveyService)

    def test_configuration_validation_missing_username_raises_exception(self):
        del self.configuration_object['MONGDB_USER']
        with self.assertRaises(exceptions.PattanMongoSurveyConfigurationError) as exc:
            MongoSurveyService(self.configuration_object)
        self.assertEqual(exc.exception.message, 'The following key(s) are missing MONGDB_USER')

    def test_configuration_validation_missing_password_raises_exception(self):
        del self.configuration_object['MONGDB_PASSWD']
        with self.assertRaises(exceptions.PattanMongoSurveyConfigurationError) as exc:
            MongoSurveyService(self.configuration_object)
        self.assertEqual(exc.exception.message, 'The following key(s) are missing MONGDB_PASSWD')

    def test_configuration_validation_missing_host_raises_exception(self):
        del self.configuration_object['MONGDB_HOST']
        with self.assertRaises(exceptions.PattanMongoSurveyConfigurationError) as exc:
            MongoSurveyService(self.configuration_object)
        self.assertEqual(exc.exception.message, 'The following key(s) are missing MONGDB_HOST')

    def test_configuration_validation_missing_db_raises_exception(self):
        del self.configuration_object['MONGDB_DB']
        with self.assertRaises(exceptions.PattanMongoSurveyConfigurationError) as exc:
            MongoSurveyService(self.configuration_object)
        self.assertEqual(exc.exception.message, 'The following key(s) are missing MONGDB_DB')

    def test_configuration_validation_missing_survey_collection_raises_exception(self):
        del self.configuration_object['MONGDB_SURVEY_COLLECTION']
        with self.assertRaises(exceptions.PattanMongoSurveyConfigurationError) as exc:
            MongoSurveyService(self.configuration_object)
        self.assertEqual(exc.exception.message, 'The following key(s) are missing MONGDB_SURVEY_COLLECTION')

    def test_configuration_validation_missing_response_collection_raises_exception(self):
        del self.configuration_object['MONGDB_DB_RESPONSE_COLLECTION']
        with self.assertRaises(exceptions.PattanMongoSurveyConfigurationError) as exc:
            MongoSurveyService(self.configuration_object)
        self.assertEqual(exc.exception.message, 'The following key(s) are missing MONGDB_DB_RESPONSE_COLLECTION')
