from django.shortcuts import redirect, render
from blog.models import Post, Category, Comment
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator


def blogList(request):
    # Get all published posts
    blog_count = Post.objects.filter(status="published")
    blog = Post.objects.filter(status="published").order_by("-date")

    # Get featured posts
    featured_blog = Post.objects.filter(featured=True, status="published").order_by("-date")[:6]

    # Get active categories with post counts
    categories = Category.objects.filter(active=True).annotate(
        post_count=Count('post', filter=Q(post__status='published'))
    ).order_by('title')

    # Search functionality
    query = request.GET.get("q")
    if query:
        blog = blog.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    # Category filtering
    category_slug = request.GET.get("category")
    if category_slug:
        blog = blog.filter(category__slug=category_slug)

    # Sorting options
    sort_by = request.GET.get("sort", "latest")
    if sort_by == "popular":
        blog = blog.order_by("-views", "-date")
    elif sort_by == "oldest":
        blog = blog.order_by("date")
    else:  # latest (default)
        blog = blog.order_by("-date")

    # Enhanced pagination
    paginator = Paginator(blog, 12)  # Show 12 posts per page for better grid layout
    page_number = request.GET.get('page')
    blog = paginator.get_page(page_number)

    context = {
        "query": query,
        "categories": categories,
        "blog_count": blog_count,
        "blog": blog,
        "featured_blog": featured_blog,
        "sort_by": sort_by,
        "category_slug": category_slug,
    }
    return render(request, 'users/bloglist.html', context)

def blogDetail(request, pid):
    try:
        post = Post.objects.get(status="published", pid=pid)
    except Post.DoesNotExist:
        messages.error(request, "The requested article was not found.")
        return redirect("blog:blog-list")

    # Get active comments
    comments = Comment.objects.filter(post=post, active=True).order_by("-date")

    # Get recent blogs (excluding current post)
    blogs = Post.objects.filter(status="published").exclude(pid=pid).order_by("-date")[:10]

    # Get related blogs from same category (excluding current post)
    related_blogs = Post.objects.filter(
        category=post.category,
        status="published"
    ).exclude(pid=pid).order_by("-views", "-date")[:6]

    # If not enough related blogs from same category, get popular posts
    if related_blogs.count() < 4:
        additional_blogs = Post.objects.filter(
            status="published"
        ).exclude(pid=pid).exclude(
            pid__in=[blog.pid for blog in related_blogs]
        ).order_by("-views", "-date")[:6-related_blogs.count()]
        related_blogs = list(related_blogs) + list(additional_blogs)

    # Increment view count (only once per session)
    session_key = f'viewed_post_{post.pid}'
    if not request.session.get(session_key, False):
        post.views += 1
        post.save()
        request.session[session_key] = True

    # Handle comment submission
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        comment_text = request.POST.get("comment")
        email = request.POST.get("email")

        if full_name and comment_text and email:
            Comment.objects.create(
                full_name=full_name,
                email=email,
                comment=comment_text,
                post=post
            )
            messages.success(request, f"Thank you {full_name}! Your comment has been submitted for review.")
            return redirect("blog:blog-detail", post.pid)
        else:
            messages.error(request, "Please fill in all required fields.")

    # Get previous and next posts for navigation
    try:
        previous_post = Post.objects.filter(
            status="published",
            date__lt=post.date
        ).order_by("-date").first()
    except:
        previous_post = None

    try:
        next_post = Post.objects.filter(
            status="published",
            date__gt=post.date
        ).order_by("date").first()
    except:
        next_post = None

    context = {
        "post": post,
        "comment": comments,
        "blogs": blogs,
        "related_blogs": related_blogs,
        "previous_post": previous_post,
        "next_post": next_post,
    }
    return render(request, 'users/blogdetail.html', context)


def category_detail(request, slug):
    category = Category.objects.get(slug=slug)
    blog_count = Post.objects.filter(category=category, status="published")
    blog = Post.objects.filter(category=category, status="published")
    categories = Category.objects.filter(active=True)
    
    query = request.GET.get("q")
    if query:
        blog = blog.filter(
            Q(title__icontains=query)).distinct()

    paginator = Paginator(blog, 2)
    page_number = request.GET.get('page')
    blog = paginator.get_page(page_number)
    
    

    context = {
        "blog_count": blog_count,
        "query": query,
        "blog": blog,
        "category": category,
        "categories": categories,
    }
    return render(request, 'blog/category-detail.html', context)
