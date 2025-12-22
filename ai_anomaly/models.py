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
    Stores user behavior metrics used for AI-based anomaly detection.
    Each record represents activity aggregated over a short time window.
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
        verbose_name = "User Activity"
        verbose_name_plural = "User Activities"

    def __str__(self):
        return (
            f"{self.user.email} | "
            f"D:{self.downloads} "
            f"F:{self.files} "
            f"FL:{self.failed_logins} "
            f"@ {self.created_at.strftime('%Y-%m-%d %H:%M')}"
        )

    @property
    def feature_vector(self):
        """
        Returns activity as a feature vector for ML models
        """
        return [self.downloads, self.files, self.failed_logins]

    def is_suspicious(self, threshold=40):
        """
        Simple rule-based check (fallback / demo support)
        """
        return (
            self.downloads > threshold or
            self.files > threshold or
            self.failed_logins > threshold
        )
