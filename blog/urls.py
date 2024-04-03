from django.urls import path
from blog import views

app_name = 'blog'

urlpatterns = [
    path('', views.blogList, name="blog-list"),
    path('<pid>', views.blogDetail, name="blog-detail"),
    path('category/<slug>/', views.category_detail, name="category_detail"),


]
