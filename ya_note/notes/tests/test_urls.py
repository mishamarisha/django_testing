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

    def test_pages_for_all_users(self):
        urls = ('notes:home', 'users:login', 'users:logout', 'users:signup')
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_list(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_only_author(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.other_user, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:detail', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
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
