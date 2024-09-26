from django.db import models

# Create your models here.
class FileUpload(models.Model):
    file = models.FileField()
    uploaded_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.uploaded_on} {self.file.name}"
    
    def get_file_name(self):
        return self.file.name

