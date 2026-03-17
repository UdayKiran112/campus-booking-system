from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('me/', views.current_user_view, name='current-user'),
    path('profile/update/', views.update_profile_view, name='update-profile'),
    path('change-password/', views.change_password_view, name='change-password'),
    path('users/', views.UserListView.as_view(), name='user-list'),
]
