from django.urls import path,include
from . import views 

app_name = 'users'

urlpatterns = [
    path('', views.home, name='users-home'),
    path('about/', views.aboutus, name='aboutus'),
    path('contactus/', views.contactus, name='contactus'),
    path('register/',views.register,name='users-register'),
    path('success/', views.success, name='success'),
    path('destination/<int:id>/',views.destination,name='users-destination'),
    path('search/',views.search, name="search"),
    path('package/<int:package_id>/', views.detail_package, name='users-detail-package'),
    path('bookings/',views.bookings,name='users-bookings'),
    path('activate/<uid64>/<token>',views.ActivateAccountView.as_view(),name='activate'),

]

