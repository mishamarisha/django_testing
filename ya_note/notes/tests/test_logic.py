from http import HTTPStatus

from django.contrib.auth import get_user_model
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
        cls.generated_slug = slugify(cls.NOTE_TITLE)[:cls.MAX_SLUG_LENGTH]
        cls.new_generated_slug = slugify(
            cls.NOTE_TITLE_EDIT)[:cls.MAX_SLUG_LENGTH]
        cls.add_url = reverse('notes:add')
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.redirect_url = reverse('notes:success')

    def test_annonymous_user_cant_create_note(self):
        note_count_before_post = Note.objects.count()
        self.client.post(self.add_url, data=self.form_data)
        note_count_after_post = Note.objects.count()
        self.assertEqual(note_count_before_post, note_count_after_post)

    def test_auth_user_create_note(self):
        note_list_before_post = set(Note.objects.all())
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note_list_after_post = set(Note.objects.all())
        new_note = note_list_after_post.difference(note_list_before_post)
        self.assertEqual(len(new_note), 1)
        note = new_note.pop()
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.title, self.NOTE_TITLE_EDIT)
        self.assertEqual(note.text, self.NOTE_TEXT_EDIT)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.redirect_url)
        self.assertFalse(
            Note.objects.filter(slug=self.generated_slug).exists())

    def test_user_cant_delete_note_of_another_user(self):
        response = self.another_user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(slug=self.generated_slug).exists())

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        note_after_edit = Note.objects.get(id=self.note.id)
        self.assertEqual(note_after_edit.text, self.form_data['text'])
        self.assertEqual(note_after_edit.title, self.form_data['title'])
        self.assertEqual(note_after_edit.author, self.note.author)
        self.assertEqual(note_after_edit.slug, self.new_generated_slug)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.another_user_client.post(
            self.edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_after_edit = Note.objects.get(slug=self.generated_slug)
        self.assertEqual(self.note.text, note_after_edit.text)
        self.assertEqual(self.note.title, note_after_edit.title)
        self.assertEqual(self.note.author, note_after_edit.author)
        self.assertEqual(self.note.slug, note_after_edit.slug)

    def test_filled_empty_slug(self):
        note_list_before_post = set(Note.objects.all())
        self.author_client.post(self.add_url, data={
            'title': self.NOTE_TITLE_EDIT,
            'text': self.NOTE_TEXT_EDIT,
            'slug': ''
        })
        note_list_after_post = set(Note.objects.all())
        new_note = note_list_after_post.difference(note_list_before_post)
        self.assertEqual(len(new_note), 1)
        note = new_note.pop()
        self.assertEqual(note.slug, self.new_generated_slug)

    def test_slug_unique(self):
        before_note_count = Note.objects.count()
        response = self.author_client.post(self.add_url, data={
            'title': self.NOTE_TITLE,
            'text': self.NOTE_TEXT,
        })
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'{self.generated_slug} - такой slug уже существует, '
            'придумайте уникальное значение!'
        )
        self.assertEqual(Note.objects.count(), before_note_count)
