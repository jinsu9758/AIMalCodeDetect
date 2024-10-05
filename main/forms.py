from django.forms import ModelForm
from admin_page.models import FileUpload

class FileUploadForm(ModelForm):
    class Meta:
        model = FileUpload
        fields = ['file']
