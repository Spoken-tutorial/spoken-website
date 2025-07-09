from builtins import object
class HealthRouter(object):
    """
        A router to manage database operations in the health app.
    """
    def db_for_read(self, model, **hints):
        """
            Point all read operations on health app to spoken
            database.
        """
        if model._meta.app_label == 'health_app':
            return 'healthdb'
        return None