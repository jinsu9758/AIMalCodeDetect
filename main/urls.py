from django.urls import path
from .views import file_download_view, index
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('download/', file_download_view, name='file_download'),
    path('', index, name="index"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
