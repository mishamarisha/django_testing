import pytest
from django.conf import settings
from django.urls import reverse

from news.models import News, Comment
from news.forms import CommentForm


@pytest.mark.django_db
@pytest.mark.usefixtures('news_list')
def test_news_on_homepage_count(client):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('news_list', 'comment_list')
@pytest.mark.parametrize(
    'model_class, date_field',
    [
        (News, "date"),
        (Comment, "created"),
    ],
)
def test_order(client, model_class, date_field):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    filtered_list = [
        obj for obj in object_list if isinstance(obj, model_class)
    ]
    all_dates = [getattr(obj, date_field) for obj in filtered_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_commentform_for_auth_user(news, not_author_client):
    url = reverse('news:detail', args=(news.id,))
    response = not_author_client.get(url)
    assert ('form' in response.context) is True
    assert isinstance(response.context.get('form'), CommentForm)


@pytest.mark.django_db
def test_commentform_for_anonymous_user(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert ('form' in response.context) is False
