from tests.utils import assert_redirects_to_login
from tests import factories as f


def test_student_bactch_create(client, db, reverse):
    url = reverse('events:add_batch')
    user = f.create_user()

    # should require login
    response = client.get(url)
    assert_redirects_to_login(response, next=url)

    # should require user to be in 'Organiser' group for this view to be available
    client.login(user)
    response = client.get(url)
    assert_redirects_to_login(response, next=url)

    user.groups.add(f.create_group(name='Organiser'))
    response = client.get(url)
    assert response.status_code == 200
