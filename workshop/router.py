class WorkshopRouter(object):
    """A router to manage database operations in the cdeep app.
    """

    def db_for_read(self, model, **hints):
        """Point all read operations on cdeep app to spoken
        database.
        """
        if model._meta.app_label == 'workshop':
            return 'workshop_info'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'workshop':
            return 'workshop_info'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, model):
        return True
