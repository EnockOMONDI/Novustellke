from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from taggit.managers import TaggableManager
from html import unescape
from django.utils.html import strip_tags
from shortuuid.django_fields import ShortUUIDField
from pyuploadcare.dj.models import ImageField
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField


BLOG_PUBLISH_STATUS = (
	("draft", "draft"),
	("in_review", "In Review"),
	("published", "Published"),
)


class Category(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-id']
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title 
        
    
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    image = ImageField(blank=True, null=True, manual_crop="4:4",)
    title = models.CharField(max_length=1000)
    excerpt = RichTextField(config_name='minimal', blank=True, null=True, help_text="Brief description of the post")
    content = RichTextField(config_name='blog', help_text="Main blog content with rich text formatting")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = TaggableManager()
    status = models.CharField(choices=BLOG_PUBLISH_STATUS, max_length=100, default="in_review")
    featured = models.BooleanField(default=False)
    trending = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    pid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")

    class Meta:
        verbose_name = "Posts"
        verbose_name_plural = "Posts "
    
    def __str__(self):
        return self.title[0:10]

    class Meta:
        ordering = ['-date']

    def get_read_time(self):
        string = self.content + unescape(strip_tags(self.content))
        total_words = len((string).split())

        return round(total_words / 200)

    def get_excerpt(self):
        """Return excerpt if available, otherwise generate from content"""
        if self.excerpt:
            return self.excerpt
        # Auto-generate excerpt from content (first 150 characters)
        clean_content = strip_tags(self.content)
        return clean_content[:150] + "..." if len(clean_content) > 150 else clean_content

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    full_name = models.CharField(max_length=1000)
    email = models.EmailField()
    comment = RichTextField(config_name='minimal', help_text="Comment content with basic formatting")
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.comment[0:20]