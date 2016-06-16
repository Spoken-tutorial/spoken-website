# -*- coding: utf-8 -*-

# Standard Library
import functools

# Third Party Stuff
import mock
import pytest


class PartialMethodCaller:
    def __init__(self, obj, **partial_params):
        self.obj = obj
        self.partial_params = partial_params

    def __getattr__(self, name):
        return functools.partial(getattr(self.obj, name), **self.partial_params)


@pytest.fixture(autouse=True, scope='function')
def cleared_cache():
    """Fixture that exposes django cache, which is empty to start with.

    This fixture also makes sures that cache is cleared before running each and every test case.
    """
    from django.core.cache import cache
    cache.clear()
    return cache


@pytest.fixture
def client():
    from django.test.client import Client

    class _Client(Client):
        def login(self, user=None, backend="hackathon.backends.MyCustomBackend", **credentials):
            if user is None:
                return super(_Client, self).login(**credentials)

            with mock.patch('django.contrib.auth.authenticate') as authenticate:
                user.backend = backend
                authenticate.return_value = user
                return super(_Client, self).login(**credentials)

        @property
        def json(self):
            return PartialMethodCaller(obj=self, content_type='application/json;charset="utf-8"')

    return _Client()


@pytest.fixture
def outbox():
    from django.core import mail
    return mail.outbox


@pytest.fixture
def reverse():
    from django.core.urlresolvers import reverse
    return reverse
