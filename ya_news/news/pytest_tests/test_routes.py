from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, client_name, status',
    [
        (
            reverse('news:home'),
            pytest.lazy_fixture('default_client'),
            HTTPStatus.OK
        ),
        (
            reverse('users:login'),
            pytest.lazy_fixture('default_client'),
            HTTPStatus.OK
        ),
        (
            reverse('users:logout'),
            pytest.lazy_fixture('default_client'),
            HTTPStatus.OK
        ),
        (
            reverse('users:signup'),
            pytest.lazy_fixture('default_client'),
            HTTPStatus.OK
        ),
        (
            reverse('news:detail', args=(pytest.lazy_fixture('news').id,)),
            pytest.lazy_fixture('default_client'),
            HTTPStatus.OK
        ),
        (
            reverse('news:edit', args=(pytest.lazy_fixture('comment').id,)),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            reverse('news:delete', args=(pytest.lazy_fixture('comment').id,)),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            reverse('news:edit', args=(pytest.lazy_fixture('comment').id,)),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            reverse('news:delete', args=(pytest.lazy_fixture('comment').id,)),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        )
    ]
)
def test_pages_availability(url, client_name, status):
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
