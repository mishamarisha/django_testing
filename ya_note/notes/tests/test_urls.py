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
        urls_args_clients_status = [
            ('notes:home', None, None, HTTPStatus.OK),
            ('users:login', None, None, HTTPStatus.OK),
            ('users:logout', None, None, HTTPStatus.OK),
            ('users:signup', None, None, HTTPStatus.OK),
            ('notes:list', None, self.author, HTTPStatus.OK),
            ('notes:edit', (self.note.slug,), self.author,
             HTTPStatus.OK),
            ('notes:detail', (self.note.slug,), self.author,
             HTTPStatus.OK),
            ('notes:delete', (self.note.slug,), self.author,
             HTTPStatus.OK),
            ('notes:edit', (self.note.slug,), self.other_user,
             HTTPStatus.NOT_FOUND),
            ('notes:detail', (self.note.slug,), self.other_user,
             HTTPStatus.NOT_FOUND),
            ('notes:delete', (self.note.slug,), self.other_user,
             HTTPStatus.NOT_FOUND),
        ]

        for (
            url_name,
            args,
            user,
            expected_status
        ) in urls_args_clients_status:
            with self.subTest(
                url=url_name, user=user, status=expected_status
            ):
                url = (reverse(url_name, args=args) if args else reverse(
                    url_name))
                if user:
                    client = self.client
                    client.force_login(user)
                    response = client.get(url)
                else:
                    response = self.client.get(url)
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
