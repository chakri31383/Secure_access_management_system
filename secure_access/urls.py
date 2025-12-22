from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),
    path('files/', include('files.urls')),  # ✅ namespace added
    path('chat/', include(('chat.urls', 'chat'), namespace='chat')),
    path('payments/', include('payments.urls')),
    path('ai/', include(('ai_anomaly.urls', 'ai_anomaly'), namespace='ai_anomaly')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
