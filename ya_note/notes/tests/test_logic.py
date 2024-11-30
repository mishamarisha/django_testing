from pytils.translit import slugify
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.db import IntegrityError

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.form_data = {
            'title': 'Заголовок заметки',
            'text': 'Текст заметки.'
        }
        cls.url = reverse('notes:add')

    def test_annonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_auth_user_create_note(self):
        user = User.objects.create(username='Test AuthUser')
        auth_client = Client()
        auth_client.force_login(user)
        response = auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.author, user)


class TestNoteEditDelete(TestCase):

    NOTE_TITLE = 'Название заметки'
    NOTE_TEXT = 'Текст заметки. '
    NOTE_TITLE_EDIT = 'Новое название'
    NOTE_TEXT_EDIT = 'Новый текст заметки.'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.another_user = User.objects.create(username='Другой пользователь')
        cls.another_user_client = Client()
        cls.another_user_client.force_login(cls.another_user)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author
        )
        cls.form_data = {
            'title': cls.NOTE_TITLE_EDIT,
            'text': cls.NOTE_TEXT_EDIT
        }
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.redirect_url = reverse('notes:success')

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.redirect_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.another_user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT_EDIT)
        self.assertEqual(self.note.title, self.NOTE_TITLE_EDIT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.another_user_client.post(
            self.edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.title, self.NOTE_TITLE)


class TestSlugCreat(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор Заметок')
        cls.title = 'Название заметки'
        cls.generated_slug = slugify(cls.title)[:cls.MAX_SLUG_LENGTH]

    def test_filled_empty_slug(self):
        self.client.force_login(self.author)
        ready_slug = 'test_note_1'
        slugs_id = (
            (ready_slug, ready_slug, 0),
            (None, self.generated_slug, 1)
        )
        for slug, expected_slug, id in slugs_id:
            Note.objects.create(
                title=self.title,
                text='Текст заметки.',
                author=self.author,
                slug=slug
            )
            with self.subTest(slug=slug, expected_slug=expected_slug, id=id):
                response = self.client.get(reverse('notes:list'))
                note = response.context['object_list'][id]
                self.assertEqual(expected_slug, note.slug)

    def test_slug_unique(self):
        Note.objects.create(
            title=self.title,
            text='Первая заметка.',
            author=self.author,
        )
        with self.assertRaises(IntegrityError):
            Note.objects.create(
                title=self.title,
                text='Вторая заметка.',
                author=self.author,
            )
