from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
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
        cls.default_client = Client()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.other_user_client = Client()
        cls.other_user_client.force_login(cls.other_user)

    def test_status_code_for_different_users(self):
        urls_clients_status = [
            (reverse('notes:home'), self.default_client, HTTPStatus.OK),
            (reverse('users:login'), self.default_client, HTTPStatus.OK),
            (reverse('users:logout'), self.default_client, HTTPStatus.OK),
            (reverse('users:signup'), self.default_client, HTTPStatus.OK),
            (reverse('notes:list'), self.author_client, HTTPStatus.OK),
            (reverse('notes:edit', args=(self.note.slug,)),
             self.author_client, HTTPStatus.OK),
            (reverse('notes:detail', args=(self.note.slug,)),
             self.author_client, HTTPStatus.OK),
            (reverse('notes:delete', args=(self.note.slug,)),
             self.author_client, HTTPStatus.OK),
            (reverse('notes:edit', args=(self.note.slug,)),
             self.other_user_client, HTTPStatus.NOT_FOUND),
            (reverse('notes:detail', args=(self.note.slug,)),
             self.other_user_client, HTTPStatus.NOT_FOUND),
            (reverse('notes:delete', args=(self.note.slug,)),
             self.other_user_client, HTTPStatus.NOT_FOUND),
        ]

        for (
            url,
            client,
            expected_status
        ) in urls_clients_status:
            with self.subTest(
                url=url, client=client, status=expected_status
            ):
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
                response = self.default_client.get(url)
                self.assertRedirects(response, redirect_url)
