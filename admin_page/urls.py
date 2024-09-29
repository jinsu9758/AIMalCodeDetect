from django.urls import path
from .views import file_upload_view, admin_page, recieve_result, reset_result, get_chart_data
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin_page/upload', file_upload_view, name='file_upload'),
    path('admin_page/', admin_page, name='admin_page'),
    path('admin_page/recieve_result', recieve_result, name='recieve_result'),
    path('admin_page/reset_result', reset_result, name='reset_result'),
    path('api/chart-data/', get_chart_data, name='chart-data'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
