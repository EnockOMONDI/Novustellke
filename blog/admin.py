from django.contrib import admin
from blog.models import Post, Comment, Category

@admin.register(Post)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'status', 'category', 'user', 'featured', 'trending', 'date')
    list_editable = ['status', 'category', 'featured', 'trending']
    list_filter = ('category', 'status', 'featured', 'trending')
    search_fields = ['title', 'content']
    readonly_fields = ['views', 'date', 'pid']
    
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
    list_filter = ('active', 'date')
    search_fields = ['comment', 'full_name', 'email']
    
    def get_comment(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    get_comment.short_description = 'Comment'