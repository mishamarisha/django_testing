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
@pytest.mark.parametrize(
    'client_fixture, form_on_page',
    (
        ('client', False),
        ('not_author_client', True),)
)
def test_commentform_availability(request, client_fixture, form_on_page, news):
    client = request.getfixturevalue(client_fixture)
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    form = 'form' in response.context
    assert form == form_on_page
    if form_on_page:
        assert isinstance(response.context.get('form'), CommentForm)
