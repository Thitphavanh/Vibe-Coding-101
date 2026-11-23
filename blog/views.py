from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Post


def index(request):
    latest_posts = (
        Post.objects.filter(status="published")
        .select_related("category", "author")
        .order_by("-published_at")[:6]
    )
    featured = (
        Post.objects.filter(status="published", is_featured=True)
        .select_related("category", "author")
        .order_by("-published_at")[:3]
    )
    context = {
        "latest_posts": latest_posts,
        "featured": featured,
    }
    return render(request, "index.html", context)


def post_list(request):
    posts = Post.objects.filter(status="published").select_related("category", "author")

    q = request.GET.get("q", "")
    if q:
        posts = posts.filter(
            Q(title__icontains=q) | Q(summary__icontains=q) | Q(content__icontains=q)
        )

    active_category = request.GET.get("category", "")
    if active_category:
        posts = posts.filter(category__slug=active_category)

    paginator = Paginator(posts, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "q": q,
        "active_category": active_category,
        "featured": Post.objects.filter(status="published", is_featured=True)
        .select_related("category", "author")
        .order_by("-published_at")[:3],
    }
    return render(request, "blog/post_list.html", context)


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.select_related("category", "author"),
        slug=slug,
        status="published",
    )

    Post.objects.filter(pk=post.pk).update(views=F("views") + 1)
    post.refresh_from_db(fields=["views"])

    related_posts = Post.objects.none()
    if post.category_id:
        related_posts = (
            Post.objects.filter(status="published", category=post.category)
            .exclude(pk=post.pk)
            .select_related("category", "author")
            .order_by("-published_at")[:3]
        )

    prev_post = (
        Post.objects.filter(status="published", published_at__lt=post.published_at)
        .order_by("-published_at")
        .first()
    )
    next_post = (
        Post.objects.filter(status="published", published_at__gt=post.published_at)
        .order_by("published_at")
        .first()
    )

    context = {
        "post": post,
        "related_posts": related_posts,
        "prev_post": prev_post,
        "next_post": next_post,
    }
    return render(request, "blog/post_detail.html", context)
