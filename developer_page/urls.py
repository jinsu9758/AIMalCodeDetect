from django.urls import path
from .views import file_analysis_view, developer_page, recieve_result, reset_result, get_chart_data, confirm_upload_view
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('developer_page/analysis', file_analysis_view, name='file_analysis'),
    path('developer_page/confirm_upload', confirm_upload_view, name='confirm_upload'),
    path('developer_page/', developer_page, name='developer_page'),
    path('developer_page/recieve_result', recieve_result, name='recieve_result'),
    path('developer_page/reset_result', reset_result, name='reset_result'),
    path('api/chart-data/', get_chart_data, name='chart-data'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
