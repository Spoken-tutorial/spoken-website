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
    

class CertificateBatch(models.Model):
    TYPE_CHOICES = (
        (1, "TEST"),
        (2, "TRAINING")
    )

    STATUS_CHOICES = (
        (0, "QUEUED"),
        (1, "RUNNING"),
        (2, "DONE"),
        (3, "FAILED"),
    )

    batch_type = models.IntegerField(choices=TYPE_CHOICES)
    test = models.ForeignKey("events.Test", null=True, blank=True, on_delete=models.CASCADE)
    training = models.ForeignKey("events.TrainingRequest", null=True, blank=True, on_delete=models.CASCADE)

    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    rq_job_id = models.CharField(max_length=128, blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    output_path = models.TextField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)