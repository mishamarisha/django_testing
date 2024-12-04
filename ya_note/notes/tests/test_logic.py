from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):

    MAX_SLUG_LENGTH = Note._meta.get_field('slug').max_length
    NOTE_TITLE = 'Название заметки'
    NOTE_TEXT = 'Текст заметки. '
    NOTE_TITLE_EDIT = 'Новое название'
    NOTE_TEXT_EDIT = 'Обновлённый текст заметки.'

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
        cls.generated_slug = slugify(cls.title)[:cls.MAX_SLUG_LENGTH]
        cls.add_url = reverse('notes:add')
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.redirect_url = reverse('notes:success')

    def test_annonymous_user_cant_create_note(self):
        note_count_before_post = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        note_count_after_post = Note.objects.count()
        self.assertEqual(note_count_before_post, note_count_after_post)

    def test_auth_user_create_note(self):
        note_count_before_post = Note.objects.count()
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note_count_after_post = Note.objects.count()
        self.assertEqual(note_count_before_post, note_count_after_post)
        note = Note.objects.get(slug=self.generated_slug)
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.redirect_url)
        with self.assertRaises(Note.DoesNotExist):
            Note.objects.get(slug=self.generated_slug)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.another_user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(slug=self.generated_slug)
        self.assertIsNotNone(note)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT_EDIT)
        self.assertEqual(self.note.title, self.NOTE_TITLE_EDIT)
        self.assertEqual(self.note.author, self.author)
        self.assertEqual(self.note.slug, self.generated_slug)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.another_user_client.post(
            self.edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.author, self.author)
        self.assertEqual(self.note.slug, self.generated_slug)

    def test_filled_empty_slug(self):
        self.client.force_login(self.author)
        ready_slug = 'test_note_1'
        slugs_id = (
            (ready_slug, ready_slug),
            (None, self.generated_slug)
        )
        for slug, expected_slug in slugs_id:
            self.author_client.post(self.create_url, data={
                'title': self.NOTE_TITLE,
                'text': self.NOTE_TEXT,
                'slug': slug
            })
            with self.subTest(expected_slug=expected_slug):
                note = Note.objects.get(slug=expected_slug)
                self.assertIsNotNone(note)

    def test_slug_unique(self):
        self.author_client.post(self.create_url, data={
            'title': self.NOTE_TITLE,
            'text': self.NOTE_TEXT,
        })
        with self.assertRaises(IntegrityError):
            self.author_client.post(self.create_url, data={
                'title': self.NOTE_TITLE,
                'text': self.NOTE_TEXT,
            })
