from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, args, client_name, status',
    [
        ('news:home', None, 'default_client', HTTPStatus.OK),
        ('users:login', None, 'default_client', HTTPStatus.OK),
        ('users:logout', None, 'default_client', HTTPStatus.OK),
        ('users:signup', None, 'default_client', HTTPStatus.OK),
        ('news:detail', pytest.lazy_fixture('news'), 'default_client',
         HTTPStatus.OK),
        ('news:edit', pytest.lazy_fixture('comment'), 'author_client',
         HTTPStatus.OK),
        ('news:delete', pytest.lazy_fixture('comment'), 'author_client',
         HTTPStatus.OK),
        ('news:edit', pytest.lazy_fixture('comment'), 'not_author_client',
         HTTPStatus.NOT_FOUND),
        ('news:delete', pytest.lazy_fixture('comment'), 'not_author_client',
         HTTPStatus.NOT_FOUND),
    ]
)
def test_pages_availability(url, args, client_name, status, request):
    client_name = request.getfixturevalue(client_name)
    url = reverse(url, args=(args.id,)) if args else reverse(url)
    response = client_name.get(url)
    assert response.status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_redirect_for_for_anonymous_user(name, comment, client):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    response = client.get(url)
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
