from core.models import CreatedModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель сообществ в которые
    можно публиковать статьи"""

    title = models.CharField("Название группы", max_length=200)
    slug = models.SlugField("Адрес группы", unique=True)
    description = models.TextField("Описание группы")

    class Meta:
        verbose_name_plural = "Группы"

    def __str__(self):
        """Значение выводимое при печати"""
        return f"{self.title}"


class Post(CreatedModel):
    """Модель статьи в блоге."""

    text = models.TextField("Текст поста", help_text="Введите текст поста")
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Группа",
        help_text="Группа, к которой будет относиться пост",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts",
        verbose_name="Автор"
    )
    image = models.ImageField("Картинка", upload_to="posts/", blank=True)

    def __str__(self):
        """Значение выводимое при печати"""
        return f"{self.text[:15]}"

    class Meta:
        ordering = ("-created",)
        verbose_name_plural = "Статьи"


class Comment(CreatedModel):
    """Описывает модель комментариев."""

    post = models.ForeignKey(
        Post, verbose_name="Пост", related_name="comments",
        on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        User, verbose_name="Автор", related_name="comments",
        on_delete=models.CASCADE
    )
    text = models.TextField(
        verbose_name="Текст комментария", default=None, blank=False, null=False
    )

    class Meta:
        ordering = ("-created",)
        verbose_name = "комментарий"
        verbose_name_plural = "комментарии"

    def __str__(self):
        """Определяет отображение комментария
        при преобразовании его в строку."""
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following",
        verbose_name="Автор"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="follow_unique")
        ]

    def __str__(self):
        return f"{self.author}, follower:{self.user}"
