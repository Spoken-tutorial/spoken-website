class ForumsRouter(object):
    """A router to manage database operations in the forums app.
    """

    def db_for_read(self, model, **hints):
        """Point all read operations on forums app to spoken database.
        """
        if model._meta.app_label == 'forums':
            return 'forums'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'forums':
            return 'forums'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, model):
        return True
