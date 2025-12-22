# chat/models.py  (update)
from django.db import models
from accounts.models import User

class ChatPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user.email} - {'Approved' if self.approved else 'Denied'}"

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    # receiver null => broadcast to org members; otherwise single-recipient DM
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages", null=True, blank=True)
    org_id = models.IntegerField(null=True, blank=True)   # organization scope for broadcast/org-local messages
    is_to_mainadmin = models.BooleanField(default=False)  # OrgAdmin->MainAdmin direct channel (optional)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('timestamp',)

    def __str__(self):
        if self.receiver:
            return f"{self.sender.email} -> {self.receiver.email}"
        if self.is_to_mainadmin:
            return f"{self.sender.email} -> MAINADMIN (org {self.org_id})"
        return f"{self.sender.email} -> ALL (org {self.org_id})"
