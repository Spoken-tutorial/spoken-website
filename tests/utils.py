from django.core.urlresolvers import reverse


def assert_redirects_to_login(response, next=''):
    login_url = reverse('cms:login')
    assert response.status_code == 302
    assert '%s?next=%s' % (login_url, next) in response['location']
