from settings import *

class DisableMigrations(object):
    """
    It will make test not to consider migrations for test_database creation
    """
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return 'notmigrations'

MIGRATION_MODULES = DisableMigrations()