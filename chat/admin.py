from django.contrib import admin
from .models import ChatMessage, ChatPermission

admin.site.register(ChatMessage)
admin.site.register(ChatPermission)
