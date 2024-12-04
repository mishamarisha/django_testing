from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestUrls(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор Заметки')
        cls.other_user = User.objects.create(username='Другой Пользователь')
        cls.note = Note.objects.create(
            title='Название заметки',
            text='Текст из одного предложения.',
            author=cls.author
        )

    def setUp(self):
        self.author_client = self.client
        self.author_client.force_login(self.author)
        self.other_user_client = self.client
        self.other_user_client.force_login(self.other_user)
        self.client = self.client

    def test_status_code_for_different_users(self):
        client = self.client
        urls_args_clients_status = [
            ('notes:home', None, client, HTTPStatus.OK),
            ('users:login', None, client, HTTPStatus.OK),
            ('users:logout', None, client, HTTPStatus.OK),
            ('users:signup', None, client, HTTPStatus.OK),
            ('notes:list', None, self.author_client, HTTPStatus.OK),
            (
                'notes:edit',
                self.note.slug,
                self.author_client,
                HTTPStatus.OK
            ),
            (
                'notes:detail',
                self.note.slug,
                self.author_client,
                HTTPStatus.OK
            ),
            (
                'notes:delete',
                self.note.slug,
                self.author_client,
                HTTPStatus.OK
            ),
            (
                'notes:edit',
                self.note.slug,
                self.other_user_client,
                HTTPStatus.NOT_FOUND
            ),
            (
                'notes:detail',
                self.note.slug,
                self.other_user_client,
                HTTPStatus.NOT_FOUND
            ),
            (
                'notes:delete',
                self.note.slug,
                self.other_user_client,
                HTTPStatus.NOT_FOUND
            ),
        ]
        for url, args, client, status in urls_args_clients_status:
            with self.subTest(url=url, client=client, status=status):
                if args is None:
                    url = reverse(url)
                else:
                    url = reverse(url, args=(args,))
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls_args = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,))
        )
        for name, args in urls_args:
            with self.subTest(name=name):
                if args is None:
                    url = reverse(name)
                else:
                    url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
