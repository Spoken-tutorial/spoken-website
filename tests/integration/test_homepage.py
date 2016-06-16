from tests import factories as f


def test_homepage(client, db):
    response = client.get('/')
    assert response.status_code == 200
    expected_context_keys = ['tr_rec', 'random_tutorials', 'media_url',
                             'testimonials', 'notifications', 'events']
    for k in expected_context_keys:
        assert k in response.context

    assert response.context['tr_rec'] is None

    # Given a tutorial resoure with status=1or2 (why?)
    t_resource = f.create_tutorial_resource(status=1)
    response = client.get('/')
    assert response.context['tr_rec'] == t_resource

    t_resource.status = 2
    t_resource.save()
    response = client.get('/')
    assert response.context['tr_rec'] == t_resource
