# from django.db import models
# from accounts.models import User
# from django.conf import settings
#
#
#
# class AnomalyLog(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
#     user_email = models.CharField(max_length=255, blank=True, null=True)
#     event = models.CharField(max_length=255, blank=True)
#     downloads = models.IntegerField(default=0)
#     files = models.IntegerField(default=0)
#     failed_logins = models.IntegerField(default=0)
#     risk_score = models.FloatField(default=0.0)
#     detected_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.user_email or 'anonymous'} @ {self.detected_at}: {self.risk_score}"
# # ai_anomaly/models.py
# class UserActivity(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     downloads = models.IntegerField(default=0)
#     files = models.IntegerField(default=0)
#     failed_logins = models.IntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
# ai_anomaly/models.py



from django.db import models
from django.conf import settings


class UserActivity(models.Model):
    """
    Aggregated user behavior over a short time window
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_activities"
    )

    downloads = models.PositiveIntegerField(default=0)
    files = models.PositiveIntegerField(default=0)
    failed_logins = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} | D:{self.downloads} F:{self.files} FL:{self.failed_logins}"

    def feature_vector(self):
        """
        Behavioral relationship features
        """
        downloads_per_file = self.downloads / max(self.files, 1)
        failed_login_ratio = self.failed_logins / max(self.downloads + self.files, 1)

        return [
            self.downloads,
            self.files,
            self.failed_logins,
            downloads_per_file,
            failed_login_ratio
        ]
