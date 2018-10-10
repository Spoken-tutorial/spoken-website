class MdlRouter(object):
    """
        A router to manage database operations in the mdldjango app.
    """
    def db_for_read(self, model, **hints):
        """
            Point all read operations on mdldjango app to spoken
            database.
        """
        if model._meta.app_label == 'mdldjango':
            return 'moodle'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'mdldjango':
            return 'moodle'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True
