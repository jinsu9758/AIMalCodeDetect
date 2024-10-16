from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class FileUpload(models.Model):
    file = models.FileField()
    uploaded_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.uploaded_on} {self.file.name}"
    
    def get_file_name(self):
        return self.file.name
    

class MaliciousResult(models.Model):
    check_time = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255)
    mal_rate = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        null=True, blank=True
    )
    is_success = models.BooleanField(default=True)

    def __str__(self):
        status = "Success" if self.is_success else "Fail"
        return f"{self.check_time} {self.filename} ({status}) {self.mal_rate:.2f}%" if self.mal_rate is not None else f"{self.check_time} {self.filename} ({status})"


