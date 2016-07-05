from tests import factories as f


def test_organizer_request_get(client, db, reverse):
    url = reverse('events:organiser_request')
    user = f.create_user()

    response = client.get(url)

    # requires auth
    assert response.status_code == 302
    assert 'login/?next' in response['location']

    client.login(user)

    response = client.get(url)
    assert response.status_code == 200
