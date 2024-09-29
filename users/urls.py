from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('sign_in/', views.login_view, name='sign_in'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('sign_out/', views.logout_view, name='sign_out'),
    path('profile/', views.change_pw, name='profile'),
    ]