import shutil
from http import HTTPStatus

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User
from . import const


@override_settings(MEDIA_ROOT=const.TEMP_MEDIA_ROOT)
class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username=const.USERNAME)
        cls.group = Group.objects.create(
            title=const.GROUP_TITLE,
            slug=const.GROUP_SLUG,
            description=const.GROUP_DESCRIPTION,
        )
        cls.uploaded = const.UPLOADED
        cls.post = Post.objects.create(
            text=const.POST_TEXT, author=cls.author, group=cls.group
        )
        cls.POST_EDIT_URL = reverse("posts:post_edit", args=[cls.post.id])
        cls.POST_DETAIL_URL = reverse("posts:post_detail", args=[cls.post.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(const.TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def check_post(self, post, form_data):
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.text, form_data['text'])

    def test_create_new_post(self):
        """Проверка добавления нового поста
        в базу данных."""
        posts_count = Post.objects.count()
        form_data = {
            "text": const.POST_TEXT,
            "group": self.group.id,
            "image": self.uploaded,
        }
        response = self.authorized_client.post(
            const.POST_CREATE_URL, data=form_data, follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, const.PROFILE_URL)
        lastpost = Post.objects.last()
        self.check_post(lastpost, form_data)
        self.assertTrue(
            Post.objects.filter(
                text=form_data["text"],
                image="posts/small.gif",
            ).exists()
        )

    def test_create_edit_post(self):
        """Проверка изменения поста
        в базе данных при редактировании поста."""
        posts_count = Post.objects.count()
        group_new = Group.objects.create(
            title=const.GROUP_TITLE_NEW,
            slug=const.GROUP_SLUG_NEW,
            description=const.GROUP_DESCRIPTION_NEW,
        )
        form_data = {"text": self.post.text, "group": group_new.id, }
        response = self.authorized_client.post(
            self.POST_EDIT_URL, data=form_data, follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response, self.POST_DETAIL_URL)
        lastpost = Post.objects.last()
        self.check_post(lastpost, form_data)
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
            ).exists()
        )

    def test_cant_create_anonymous(self):
        """Проверка, что незарегистрированный пользователь
        не сможет создать пост."""
        posts_count = Post.objects.count()
        form_data = {"text": const.POST_TEXT, "group": self.group.id}
        response = self.client.post(const.POST_CREATE_URL, data=form_data)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(
            response, const.LOGIN_URL + const.NEXT + const.POST_CREATE_URL
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_cant_edit_anonymous(self):
        """Проверка, что незарегистрированный пользователь
        не сможет отредактировать пост.
        """
        posts_count = Post.objects.count()
        group_new = Group.objects.create(
            title=const.GROUP_TITLE_NEW,
            slug=const.GROUP_SLUG_NEW,
            description=const.GROUP_DESCRIPTION_NEW,
        )
        form_data = {"text": self.post.text, "group": group_new.id}
        response = self.client.post(self.POST_EDIT_URL, data=form_data)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(
            response, const.LOGIN_URL + const.NEXT + self.POST_EDIT_URL
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                text=self.post.text,
                author=self.author,
                group=self.group,
            ).exists()
        )


class CommentCreateFormTests(TestCase):
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

        cls.POST_EDIT_URL = reverse("posts:post_edit", args=[cls.post.id])
        cls.POST_DETAIL_URL = reverse("posts:post_detail", args=[cls.post.id])
        cls.ADD_COMMENT_URL = reverse("posts:add_comment", args=[cls.post.id])

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_new_comment(self):
        """Проверка добавления нового комментария
        в базу данных авторизованным пользователем.
        """
        comments_count = Comment.objects.count()
        form_data = {
            "text": const.COMMENT_TEXT,
        }
        response = self.authorized_client.post(
            self.ADD_COMMENT_URL, data=form_data, follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertRedirects(response, self.POST_DETAIL_URL)
        lastcomment_text = Comment.objects.order_by("-id")[0].text
        self.assertEqual(lastcomment_text, form_data["text"])

    def test_cant_create_comment_anonymous(self):
        """Проверка, что незарегистрированный пользователь
        не сможет добавить комментарий.
        """
        comments_count = Comment.objects.count()
        form_data = {
            "text": const.COMMENT_TEXT,
        }
        response = self.client.post(self.ADD_COMMENT_URL, data=form_data)
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertRedirects(
            response, const.LOGIN_URL + const.NEXT + self.ADD_COMMENT_URL
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
