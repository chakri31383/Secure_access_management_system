# files/models.py
from django.db import models
from django.conf import settings
import os
from django.utils.functional import cached_property
import humanize
def upload_path(instance, filename):
    return os.path.join('uploads', str(instance.owner.id), filename)

class File(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    org_id = models.IntegerField(null=True, blank=True)
    file = models.FileField(upload_to=upload_path)
    filename = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True)     # comma separated
    is_public = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    shared_link = models.URLField(blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr/', blank=True, null=True)
    filesize = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


    @cached_property
    def human_size(self):
        try:
            return humanize.naturalsize(self.filesize)
        except:
            return "0 B"

    class Meta:
        ordering = ['-is_favorite', '-created_at']

    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        if self.file and not self.filename:
            self.filename = os.path.basename(self.file.name)
        if self.file:
            try:
                self.filesize = self.file.size
            except Exception:
                pass
        super().save(*args, **kwargs)
