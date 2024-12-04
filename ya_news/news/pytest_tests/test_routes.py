from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args, client_name, status',
    [
        (
            'news:home',
            None,
            pytest.lazy_fixture('default_client'),
            HTTPStatus.OK
        ),
        (
            'users:login',
            None,
            pytest.lazy_fixture('default_client'),
            HTTPStatus.OK
        ),
        (
            'users:logout',
            None,
            pytest.lazy_fixture('default_client'),
            HTTPStatus.OK
        ),
        (
            'users:signup',
            None, pytest.lazy_fixture('default_client'),
            HTTPStatus.OK
        ),
        (
            'news:detail',
            'news.id',
            pytest.lazy_fixture('default_client'),
            HTTPStatus.OK
        ),
        (
            'news:edit',
            'comment.id',
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            'news:delete',
            'comment.id',
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            'news:edit',
            'comment.id',
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            'news:delete',
            'comment.id',
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        )
    ]
)
def test_pages_availability(name, args, client_name, status, news, comment):
    if args == 'news.id':
        url = reverse(name, args=(news.id,))
    elif args == 'comment.id':
        url = reverse(name, args=(comment.id,))
    else:
        url = reverse(name)
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
