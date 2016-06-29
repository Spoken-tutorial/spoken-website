from tests import factories as f
from tests.utils import assert_redirects_to_login


def test_events_dashboard(client, db, reverse):
    url = reverse('events:events_dashboard')
    user = f.create_user()

    response = client.get(url)
    assert_redirects_to_login(response)

    client.login(user)
    response = client.get(url)
    assert response.status_code == 200
