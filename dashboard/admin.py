from django.contrib import admin
from .models import Organization, Role, ActivityLog

admin.site.register(Organization)
admin.site.register(Role)
admin.site.register(ActivityLog)
# dashboard/admin.py
from .models import JoinRequest
admin.site.register(JoinRequest)
