from django.urls import path
from .views import login_view, sign_up,logout_view, change_pw
from django.conf.urls.static import static
from django.conf import settings

app_name = 'users'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('signup/', sign_up, name='signup'),
    path('changepw/', change_pw, name='changepw'),
    path('logout/', logout_view, name='logout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)