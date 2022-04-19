from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["text"].widget.attrs[
            "placeholder"
        ] = "Введите какой нибудь текст, ну пожалуйста 😥"
        self.fields["group"].empty_label = "Выберите группу🙂"

    class Meta:
        model = Post
        labels = {"group": "Группа", "text": "Текст поста"}
        help_texts = {"group": "Выберите группу", "text": "Введите ссообщение"}
        fields = ("text", "group", "image")


class CommentForm(ModelForm):
    """Создаёт форму по модели поста."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["text"].widget.attrs[
            "placeholder"
        ] = "Введите какой нибудь текст комментария"

    class Meta:
        model = Comment
        fields = ("text",)
