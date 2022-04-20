import shutil

from django import forms
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache

from . import const
from ..forms import PostForm
from ..models import Comment, Follow, Group, Post, User


@override_settings(MEDIA_ROOT=const.TEMP_MEDIA_ROOT)
class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username=const.USERNAME)
        cls.group = Group.objects.create(
            title=const.GROUP_TITLE,
            slug=const.GROUP_SLUG,
            description=const.GROUP_DESCRIPTION,
        )
        cls.group_2 = Group.objects.create(
            title=const.GROUP_TITLE_NEW,
            slug=const.GROUP_SLUG_NEW,
            description=const.GROUP_DESCRIPTION_NEW,
        )

        cls.uploaded = const.UPLOADED
        cls.post = Post.objects.create(
            author=cls.user,
            text=const.POST_TEXT,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.POST_DETAIL_URL = reverse("posts:post_detail", args=[cls.post.id])
        cls.POST_EDIT_URL = reverse("posts:post_edit", args=[cls.post.id])
        cls.form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(const.TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_post_context(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.image, self.post.image)

    def test_show_correct_context(self):
        urls = [
            const.INDEX_URL,
            const.GROUP_LIST_URL,
            const.PROFILE_URL,
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(len(response.context["page_obj"]), 1)
                post = response.context["page_obj"][0]
                self.check_post_context(post)

    def test_detail_page_show_correct(self):
        response = self.authorized_client.get(self.POST_DETAIL_URL)
        self.check_post_context(response.context["post"])

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(const.PROFILE_URL)
        self.assertEqual(self.user, response.context["author"])

    def test_group_list_show_correct_context(self):
        response = self.authorized_client.get(const.GROUP_LIST_URL)
        self.assertEqual(self.group, response.context["group"])
        self.assertEqual(self.group.title, const.GROUP_TITLE)
        self.assertEqual(self.group.slug, const.GROUP_SLUG)
        self.assertEqual(self.group.description, const.GROUP_DESCRIPTION)

    def test_new_post_in_another_group(self):
        """Наличие поста в другой группе"""
        self.assertNotIn(
            self.post,
            self.authorized_client.get(
                const.GROUP_LIST_URL_2).context["page_obj"],
        )

    def test_edit_page_correct_context(self):
        response = self.authorized_client.get(self.POST_EDIT_URL)
        self.assertIsInstance(response.context.get("form"), PostForm)
        self.assertEqual(response.context.get("title"), "Редактировать запись")
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)
        is_edit = response.context["is_edit"]
        self.assertTrue("is_edit")
        self.assertIsInstance(is_edit, bool)

    def test_create_page_correct_context(self):
        response = self.authorized_client.get(const.POST_CREATE_URL)
        self.assertIsInstance(response.context.get("form"), PostForm)
        self.assertEqual(response.context.get("title"), "Новый пост")
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cach(self):
        """Проверяем работу кеша."""
        response = self.authorized_client.get(const.INDEX_URL)
        content_post = response.content
        Post.objects.filter(id=self.post.id).delete()
        response = self.authorized_client.get(const.INDEX_URL)
        self.assertEqual(content_post, response.content)
        cache.clear()
        response = self.authorized_client.get(const.INDEX_URL)
        self.assertNotEqual(content_post, response.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username=const.USERNAME)
        cls.group = Group.objects.create(
            title=const.GROUP_TITLE,
            slug=const.GROUP_SLUG,
            description=const.GROUP_DESCRIPTION,
        )
        Post.objects.bulk_create(
            Post(text=f"Post {i}", author=cls.user, group=cls.group)
            for i in range(settings.POST_PER_PAGE + const.OTHER_PAGES)
        )

    def setUp(self) -> None:
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator_on_pages_have_ten_post(self):
        """Количество постов на страницах не больше 10 штук."""
        urls = [
            [const.INDEX_URL, settings.POST_PER_PAGE],
            [const.GROUP_LIST_URL, settings.POST_PER_PAGE],
            [const.PROFILE_URL, settings.POST_PER_PAGE],
            [const.INDEX_URL + const.NEXT_PAGE, const.OTHER_PAGES],
            [const.GROUP_LIST_URL + const.NEXT_PAGE, const.OTHER_PAGES],
            [const.PROFILE_URL + const.NEXT_PAGE, const.OTHER_PAGES],
        ]
        for url, page_count in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(len(response.context["page_obj"]), page_count)


class CommentViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username=const.USERNAME)
        cls.group = Group.objects.create(
            title=const.GROUP_TITLE,
            slug=const.GROUP_SLUG,
            description=const.GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=const.POST_TEXT, author=cls.author, group=cls.group
        )
        cls.comment = Comment.objects.create(
            author=cls.author, text=const.COMMENT_TEXT, post=cls.post
        )
        cls.POST_DETAIL_URL = reverse("posts:post_detail", args=[cls.post.id])

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_comment_view(self):
        """Шаблоны post_detail отображают созданный комментарий на
        странице поста.
        """
        response = self.authorized_client.get(self.POST_DETAIL_URL)
        first_object = response.context.get("comments")[0]
        comment_post_0 = first_object
        self.assertEqual(comment_post_0, self.comment)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username=const.USERNAME)
        cls.group = Group.objects.create(
            title=const.GROUP_TITLE,
            slug=const.GROUP_SLUG,
            description=const.GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=const.POST_TEXT, author=cls.author, group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.user_1 = User.objects.create_user(username=const.USERNAME_ALTER)
        self.authorized_client_not_author_1 = Client()
        self.authorized_client_not_author_1.force_login(self.user_1)
        self.user_2 = User.objects.create_user(username=const.USERNAME_ALTER2)
        self.authorized_client_not_author_2 = Client()
        self.authorized_client_not_author_2.force_login(self.user_2)

    def test_follower_view(self):
        """Новая запись пользователя появляется в ленте
        тех, кто на него подписан.
        """
        Follow.objects.create(user=self.user_1, author=self.author)
        new_post_author = Post.objects.create(
            text=const.POST_TEXT, author=self.author, group=self.group
        )
        response = self.authorized_client_not_author_1.get(
            const.FOLLOW_INDEX_URL)
        first_object = response.context.get("page_obj").object_list[0]
        self.assertEqual(first_object, new_post_author)

    def test_not_follower_view(self):
        """Новая запись пользователя не появляется в ленте
        тех, кто на него не подписан.
        """
        Follow.objects.create(user=self.user_2, author=self.user_1)
        Post.objects.create(text=const.POST_TEXT,
                            author=self.user_1, group=self.group)
        new_post_author = Post.objects.create(
            text=const.POST_TEXT, author=self.author, group=self.group
        )
        response = self.authorized_client_not_author_2.get(
            const.FOLLOW_INDEX_URL)
        first_object = response.context.get("page_obj").object_list[0]
        self.assertNotEqual(first_object, new_post_author)
