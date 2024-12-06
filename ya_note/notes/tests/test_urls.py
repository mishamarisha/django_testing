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
        urls_clients_status = [
            (reverse('notes:home'), None, HTTPStatus.OK),
            (reverse('users:login'), None, HTTPStatus.OK),
            (reverse('users:logout'), None, HTTPStatus.OK),
            (reverse('users:signup'), None, HTTPStatus.OK),
            (reverse('notes:list'), self.author, HTTPStatus.OK),
            (reverse('notes:edit', args=(self.note.slug,)), self.author,
             HTTPStatus.OK),
            (reverse('notes:detail', args=(self.note.slug,)), self.author,
             HTTPStatus.OK),
            (reverse('notes:delete', args=(self.note.slug,)), self.author,
             HTTPStatus.OK),
            (reverse('notes:edit', args=(self.note.slug,)), self.other_user,
             HTTPStatus.NOT_FOUND),
            (reverse('notes:detail', args=(self.note.slug,)), self.other_user,
             HTTPStatus.NOT_FOUND),
            (reverse('notes:delete', args=(self.note.slug,)), self.other_user,
             HTTPStatus.NOT_FOUND),
        ]

        for (
            url,
            user,
            expected_status
        ) in urls_clients_status:
            with self.subTest(
                url=url, user=user, status=expected_status
            ):
                if user:
                    client = self.client
                    client.force_login(user)
                    response = self.client.get(url)
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
