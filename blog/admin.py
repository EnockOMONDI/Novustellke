from django.contrib import admin
from django import forms
from django.db import models
from blog.models import Post, Comment, Category
from django_ckeditor_5.widgets import CKEditor5Widget
from django_ckeditor_5.fields import CKEditor5Field

@admin.register(Post)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'status', 'category', 'user', 'featured', 'trending', 'date')
    list_editable = ['status', 'category', 'featured', 'trending']
    list_filter = ('category', 'status', 'featured', 'trending', 'date')
    search_fields = ['title', 'content', 'excerpt']
    readonly_fields = ['views', 'date', 'pid']
    date_hierarchy = 'date'

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'excerpt', 'category', 'tags', 'image')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
        ('Publishing', {
            'fields': ('status', 'featured', 'trending', 'user'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('views', 'date', 'pid'),
            'classes': ('collapse',)
        }),
    )

    # RichTextField widgets are automatically handled by the field configuration
    # No formfield_overrides needed for RichTextField

    class Media:
        css = {
            'all': ('assets/css/ckeditor5-admin.css',)
        }

    def get_title(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    get_title.short_description = 'Title'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'active')
    list_editable = ['active']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('get_comment', 'post', 'full_name', 'email', 'date', 'active')
    list_editable = ('active',)
    list_filter = ('active', 'date', 'post')
    search_fields = ['comment', 'full_name', 'email', 'post__title']
    date_hierarchy = 'date'

    fieldsets = (
        ('Comment Information', {
            'fields': ('post', 'full_name', 'email', 'comment')
        }),
        ('Moderation', {
            'fields': ('active',)
        }),
        ('System Information', {
            'fields': ('date',),
            'classes': ('collapse',)
        }),
    )

    # RichTextField widgets are automatically handled by the field configuration
    # No formfield_overrides needed for RichTextField

    def get_comment(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    get_comment.short_description = 'Comment'