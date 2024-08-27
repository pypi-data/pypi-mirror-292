class MissingSurveyId(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "MissingSurveyId, {0} ".format(self.message)
        else:
            return "MissingSurveyId the method you have called requires you provide a survey id"


class DataSaveFailure(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "DataSaveFailure, {0} ".format(self.message)
        else:
            return "DataSaveFailure changes were not saved."


class FetchResultsFailure(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "FetchResultsFailure: {0} ".format(self.message)
        else:
            return "FetchResultsFailure: unable to fetch results."


class DeleteSurveyFailure(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "DeleteSurveyFailure: {0} ".format(self.message)
        else:
            return "DeleteSurveyFailure: failed to delete the survey."


class DeleteSurveyResponseFailure(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "DeleteSurveyResponseFailure: {0} ".format(self.message)
        else:
            return "DeleteSurveyResponseFailure: failed to delete the survey."


class PattanMongoSurveyConfigurationError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "PattanMongoSurveyConfigurationError: {0} ".format(self.message)
        else:
            return '''
                PattanMongoSurveyConfigurationError: you must provide an dictionary with the following keys to configure 
                pattan-mongo-survey correctly.
                MONGDB_USER
                MONGDB_PASSWD
                MONGDB_HOST
                MONGDB_DB
                MONGDB_SURVEY_COLLECTION - collection used to store survey questions
                MONGDB_DB_RESPONSE_COLLECTION - collection used to store survey responses
            '''
