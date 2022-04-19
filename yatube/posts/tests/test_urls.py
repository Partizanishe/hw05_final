from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache


from ..models import Group, Post, User


class PostURLTests(TestCase):
    """Проверяем URL приложения Post"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user1 = User.objects.create(username="HasNoName")
        cls.test_user2 = User.objects.create(username="HasSomeName")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.test_post1 = Post.objects.create(
            author=cls.test_user1,
            text="Тестовый пост номер 1",
            group=cls.group,
        )
        cls.test_post2 = Post.objects.create(
            author=cls.test_user2,
            text="Тестовый пост номер 2",
            group=cls.group,
        )
        cls.urls_pages = [
            "/",
            "/group/test_slug/",
            "/profile/HasNoName/",
            "/posts/1/",
            "/create/",
            "/posts/1/edit/",
        ]
        cls.url_template = {
            "/": "posts/index.html",
            "/create/": "posts/create_post.html",
            "/posts/1/": "posts/post_detail.html",
            "/group/test_slug/": "posts/group_list.html",
            "/posts/1/edit/": "posts/create_post.html",
            "/profile/HasNoName/": "posts/profile.html",
        }

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.test_user1)

    def test_public_pages(self):
        """Проверяем вход незарегистрированного пользователя
        на общедоступные страницы.
        """
        for page in self.urls_pages[:4]:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_pages(self):
        """Проверяем редирект незарегистрированного пользователя
        при попытке войти на страницы для зарегистрированного ползователя.
        """
        for page in self.urls_pages[4:]:
            with self.subTest(page=page):
                redirect_url = reverse("users:login") + f"?next={page}"
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response, redirect_url)

    def test_edit_page(self):
        """Проверяем доступность страниц для автора."""
        for page in self.urls_pages:
            with self.subTest(page=page):
                response = self.author_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_page(self):
        """Проверяем доступность страниц для авторизованного пользователя."""
        for page in self.urls_pages[:5]:
            with self.subTest(page=page):
                response = self.author_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_authorized_client(self):
        """Проверяем редирект авторизованного пользователя при попытке
        войти на страницу редактирования поста другого автора.
        """
        response = self.author_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.test_post2.id})
        )
        redirect_url = reverse(
            "posts:post_detail", kwargs={"post_id": self.test_post2.id}
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, redirect_url)

    def test_unexisting_page(self):
        """Проверяем статус несуществующей страницы."""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "core/404.html")

    def test_templates(self):
        """Проверяем, что URL-адрес использует соответствующий шаблон."""
        for url, template in self.url_template.items():
            with self.subTest(template=template):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)
