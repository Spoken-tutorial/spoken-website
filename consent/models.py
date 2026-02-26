from django.conf import settings
from django.db import models


class ConsentVersion(models.Model):
    file_name = models.CharField(max_length=255)
    file_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.is_active:
            ConsentVersion.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super(ConsentVersion, self).save(*args, **kwargs)

    def __str__(self):
        return '%s (%s)' % (self.file_name, 'active' if self.is_active else 'inactive')


class UserConsent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    consent = models.ForeignKey(ConsentVersion, on_delete=models.CASCADE)
    accepted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'consent')

    def __str__(self):
        return '%s - v%s' % (self.user, self.consent_id)
gi