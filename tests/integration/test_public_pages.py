import pytest

urls_public_expected_200 = [
    '/',
    # '/robots.txt',
    # '/sitemap.xml',
    '/sitemap.html',
]


@pytest.mark.parametrize("test_url", urls_public_expected_200)
def test_page_success_reponse(client, db, test_url):
    response = client.get(test_url)
    assert response.status_code == 200
