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
    sender = models.EmailField(default='no-reply@spoken-tutorial.org')
    log_file =  models.FileField(null=True, upload_to='emails/')
    job_id = models.TextField(null=True)
    ers_job_id = models.TextField(null=True)

    def __str__(self):
        return self.subject
    

