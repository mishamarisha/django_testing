from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, client_name, status',
    [
        (pytest.lazy_fixture('home_page_url'), 'default_client',
         HTTPStatus.OK),
        (pytest.lazy_fixture('login_url'), 'default_client', HTTPStatus.OK),
        (pytest.lazy_fixture('logout_url'), 'default_client', HTTPStatus.OK),
        (pytest.lazy_fixture('signup_url'), 'default_client', HTTPStatus.OK),
        (pytest.lazy_fixture('news_detail_url'), 'default_client',
         HTTPStatus.OK),
        (pytest.lazy_fixture('comment_edit_url'), 'author_client',
         HTTPStatus.OK),
        (pytest.lazy_fixture('comment_delete_url'), 'author_client',
         HTTPStatus.OK),
        (pytest.lazy_fixture('comment_edit_url'), 'not_author_client',
         HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('comment_delete_url'), 'not_author_client',
         HTTPStatus.NOT_FOUND),
    ]
)
def test_pages_availability(url, client_name, status, request):
    client_name = request.getfixturevalue(client_name)
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
