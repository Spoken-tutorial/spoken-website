from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

class AsyncCronMail(models.Model):
    subject = models.CharField(max_length=100)
    csvfile = models.FileField(upload_to='emails/', validators=[FileExtensionValidator(['csv'])])
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT )
    status = models.BooleanField()
    report = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    message = models.TextField()
    sender = models.EmailField()
    log_file =  models.FileField(null=True, upload_to='emails/')

