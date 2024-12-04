from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


def test_user_can_create_comment(author_client, author, form_data, news):
    before_post_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    expected_url = url + '#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == (before_post_count + 1)
    new_comment = Comment.objects.get(
        text=form_data['text'], author=author, news=news)
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news.id == news.id


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    before_post_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == before_post_count


def test_author_can_edit_comment(
        author_client, form_data, comment, news, author):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, form_data)
    news_url = reverse('news:detail', args=(news.id,))
    expected_url = news_url + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news.id == news.id


def test_author_can_delete_comment(author_client, comment, news):
    before_delete_count = Comment.objects.count()
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    news_url = reverse('news:detail', args=(news.id,))
    expected_url = news_url + '#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == (before_delete_count - 1)


def test_other_user_cant_edit_comment(
        not_author_client, form_data, comment, news, author):
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == author
    assert comment.news.id == news.id


def test_other_user_cant_delete_comment(not_author_client, comment):
    before_delete_count = Comment.objects.count()
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == before_delete_count


def test_user_cant_use_bad_words(author_client, news):
    before_post_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=bad_words_data)
    assert response.status_code == 200
    form = response.context.get('form')
    assert form.errors['text'][0] == WARNING
    assert before_post_count == Comment.objects.count()
