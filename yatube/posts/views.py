from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import paginator_page


@cache_page(20, key_prefix="index_page")
def index(request):
    page_obj = paginator_page(request, Post.objects.select_related("author"))
    context = {
        "title": "Последние обновления на сайте",
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    page_obj = paginator_page(request, group.posts.select_related("group"))
    context = {"group": group, "page_obj": page_obj}
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    page_obj = paginator_page(request, author.posts.select_related("author"))
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author).exists()
    )
    context = {"author": author, "page_obj": page_obj, "following": following}
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related("author"), id=post_id)
    comments = post.comments.all().select_related("author")
    context = {
        "post": post,
        "form": CommentForm(),
        "comments": comments,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    context = {
        "title": "Новый пост",
    }
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect("posts:profile", request.user)
    context["form"] = form
    return render(request, "posts/create_post.html", context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail", post_id)
    context = {"title": "Редактировать запись", "post": post, "is_edit": True}
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post.id)
    context["form"] = form
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, id=post_id)
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.select_related("author").filter(
        author__following__user=request.user
    )
    page_obj = paginator_page(request, post_list)
    template = "posts/follow.html"
    context = {
        "title": "Посты в подписке",
        "page_obj": page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("posts:profile", author)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(user=request.user, author__username=username).delete()
    return redirect("posts:profile", username)
