import shutil
from http import HTTPStatus

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User
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
        lastpost = Post.objects.order_by("-id")[0]
        self.assertTrue(
            Post.objects.filter(
                id=lastpost.id,
                text=form_data["text"],
                author=self.author,
                group=self.group,
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
        form_data = {"text": self.post.text, "group": group_new.id}
        response = self.authorized_client.post(
            self.POST_EDIT_URL, data=form_data, follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response, self.POST_DETAIL_URL)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                text=self.post.text,
                author=self.author,
                group=group_new.id,
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
        lastcomment = Comment.objects.order_by("-id")[0]
        self.assertTrue(
            Comment.objects.filter(
                id=lastcomment.id,
                text=form_data["text"],
            ).exists()
        )

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


class FollowCreateFormTests(TestCase):
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
        cls.FOLLOW_URL = reverse("posts:profile_follow",
                                 args=[cls.author.username])
        cls.UNFOLLOW_URL = reverse(
            "posts:profile_unfollow", args=[cls.author.username])

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.user_1 = User.objects.create_user(username=const.USERNAME_ALTER)
        self.authorized_client_not_author_1 = Client()
        self.authorized_client_not_author_1.force_login(self.user_1)
        self.user_2 = User.objects.create_user(username=const.USERNAME_ALTER2)
        self.authorized_client_not_author_2 = Client()
        self.authorized_client_not_author_2.force_login(self.user_2)

    def test_create_follow(self):
        """Проверка, что авторизованный пользователь
        может подписываться на других пользователей
        """
        follow_count = Follow.objects.count()
        form_data = {"username": self.author.username}
        response = self.authorized_client_not_author_1.post(
            self.FOLLOW_URL,
            data=form_data,
            follow=True,
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertRedirects(response, const.PROFILE_URL)
        self.assertTrue(
            Follow.objects.filter(
                author=self.author, user=self.user_1).exists()
        )

    def test_create_unfollow(self):
        """Проверка, что авторизованный пользователь
        может отписываться от других пользователей
        """
        follow = Follow.objects.create(user=self.user_1, author=self.author)
        follow_count = Follow.objects.count()
        follow.delete()
        form_data = {"username": self.author.username}
        response = self.authorized_client_not_author_1.post(
            self.UNFOLLOW_URL,
            data=form_data,
            follow=True,
        )
        self.assertEqual(Follow.objects.count(), follow_count - 1)
        self.assertRedirects(response, const.PROFILE_URL)
        self.assertFalse(
            Follow.objects.filter(author=self.author,
                                  user=self.user_1).exists()
        )
