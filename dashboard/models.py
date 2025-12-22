from django.db import models
from accounts.models import User
from django.conf import settings

class Organization(models.Model):
    name = models.CharField(max_length=100)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="org_admin")
    payment_status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """
    Role name + permissions scoped to an organization (org_id as integer).
    Example: org_id=1, name='Faculty', can_view=True, can_edit=True, can_delete=True, can_chat=True
    """
    name = models.CharField(max_length=100)
    org_id = models.IntegerField(null=True, blank=True)   # matches your User.org_id design
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_chat = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'org_id')  # role name unique per organization

    def __str__(self):
        return f"{self.name} (@org {self.org_id})"

class Role(models.Model):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_chat = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.org.name}"

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.action}"
class JoinRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='join_requests')
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='join_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True)   # optional message from user
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='reviewed_join_requests')

    class Meta:
        unique_together = ('user', 'org')  # a user can have only one request per org

    def __str__(self):
        return f"{self.user.email} -> {self.org.name} ({self.status})"