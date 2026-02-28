from django.conf import settings
from django.db import models

from .utils import compute_file_hash


class Consent(models.Model):
    file = models.FileField(upload_to='consent/')
    file_hash = models.CharField(max_length=64, blank=True)
    type = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.is_active:
            Consent.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super(Consent, self).save(*args, **kwargs)
        if self.file:
            new_hash = compute_file_hash(self.file.path)
            if new_hash != self.file_hash:
                self.file_hash = new_hash
                super(Consent, self).save(update_fields=['file_hash'])

    def __str__(self):
        return '%s (%s)' % (self.file.name, 'active' if self.is_active else 'inactive')


class UserConsent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    consent = models.ForeignKey(Consent, on_delete=models.CASCADE)
    accepted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'consent')

    def __str__(self):
        return '%s - v%s' % (self.user, self.consent_id)