from django.test import Client, TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note


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
        all_notes = [
            Note(
                title=f'Заметка {index}',
                text=f'Текст заметки {index}',
                slug=f'test_note_{index}',
                author=cls.author
            )for index in range(1, cls.NOTES_COUNT_FOR_TEST + 1)
        ]
        Note.objects.bulk_create(all_notes)

    def test_note_in_object_list(self):
        response = self.author_client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        note_in_context = object_list[0]
        first_note = Note.objects.filter(author=self.author).first()
        self.assertEqual(note_in_context, first_note)

    def test_not_notes_other_author(self):
        response = self.another_user_client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        note_count = object_list.count()
        self.assertEqual(note_count, 0)

    def test_form_in_context(self):
        note = Note.objects.first()
        urls_kwarg = (('notes:add', {}), ('notes:edit', {'slug': note.slug}))
        for url, kwargs in urls_kwarg:
            with self.subTest(url=url, kwargs=kwargs):
                response = self.client.get(reverse(url, kwargs=kwargs))
                form = 'form' in response.context
                self.assertEqual(form, True)
