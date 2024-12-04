from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestUrls(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор Заметки')
        cls.other_user = User.objects.create_user(
            username='Другой Пользователь')
        cls.note = Note.objects.create(
            title='Название заметки',
            text='Текст заметки.',
            slug='test-slug',
            author=cls.author
        )

    def test_status_code_for_different_users(self):
        author_client = self.client
        author_client.force_login(self.author)
        other_user_client = self.client
        other_user_client.force_login(self.other_user)
        urls_args_clients_status = [
            ('notes:home', None, self.client, HTTPStatus.OK),
            ('users:login', None, self.client, HTTPStatus.OK),
            ('users:logout', None, self.client, HTTPStatus.OK),
            ('users:signup', None, self.client, HTTPStatus.OK),
            ('notes:list', None, author_client, HTTPStatus.OK),
            ('notes:edit', (self.note.slug,), author_client,
             HTTPStatus.OK),
            ('notes:detail', (self.note.slug,), author_client,
             HTTPStatus.OK),
            ('notes:delete', (self.note.slug,), author_client,
             HTTPStatus.OK),
            ('notes:edit', (self.note.slug,), other_user_client,
             HTTPStatus.NOT_FOUND),
            ('notes:detail', (self.note.slug,), other_user_client,
             HTTPStatus.NOT_FOUND),
            ('notes:delete', (self.note.slug,), other_user_client,
             HTTPStatus.NOT_FOUND),
        ]

        for (
            url_name,
            args,
            client,
            expected_status
        ) in urls_args_clients_status:
            with self.subTest(
                url=url_name, client=client, status=expected_status
            ):
                url = (reverse(url_name, args=args) if args else reverse(
                    url_name))
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls_args = [
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,))
        ]

        for name, args in urls_args:
            with self.subTest(name=name):
                url = reverse(name, args=args) if args else reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
