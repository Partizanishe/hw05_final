from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    """Проверяем модель"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Test Group Title Long Long Long Name",
            slug="Tes_Slug",
            description="Test Description",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Test Text Long Long Long Text",
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        expected_fields = {post: post.text[:15], group: group.title}
        for field, expected_value in expected_fields.items():
            with self.subTest(field=field):
                self.assertEqual(expected_value, str(field))

    def test_verbose_name(self):
        """Проверяем, что у моделей отображается verbose_name."""
        post = PostModelTest.post
        field_verboses = {
            "text": "Текст поста",
            "created": "Дата публикации",
            "author": "Автор",
            "group": "Группа",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text(self):
        """Проверяем, что у моделей отображается help_text"""
        post = PostModelTest.post
        field_help_text = {
            "text": "Введите текст поста",
            "group": "Группа, к которой будет относиться пост",
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(field).help_text,
                                 expected_value)
