from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestNotesContext(TestCase):

    NOTES_COUNT_FOR_TEST = 5

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор Заметок')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.another_user = User.objects.create(username='Другой пользователь')
        cls.another_user_client = Client()
        cls.another_user_client.force_login(cls.another_user)
        cls.slug = 'test_note'
        Note.objects.create(
            title='Заметка',
            text='Текст заметки',
            slug=cls.slug,
            author=cls.author
        )

    def test_note_in_object_list(self):
        response = self.author_client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        note = Note.objects.get(slug=self.slug)
        self.assertIn(note, object_list)

    def test_not_notes_other_author(self):
        response = self.another_user_client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        note = Note.objects.get(slug=self.slug)
        self.assertNotIn(note, object_list)

    def test_form_in_context(self):
        note = Note.objects.first()
        urls_kwarg = [('notes:add', None), ('notes:edit', {'slug': note.slug})]
        for url, kwargs in urls_kwarg:
            with self.subTest(url=url):
                response = self.author_client.get(reverse(url, kwargs=kwargs))
                form = response.context.get('form')
                self.assertIsInstance(form, NoteForm)
