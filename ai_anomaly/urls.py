# # ai_anomaly/urls.py
# from django.urls import path
# from . import views
#
# app_name = 'ai_anomaly'
#
# urlpatterns = [
#     path('monitor/', views.monitor, name='monitor'),
#     path('monitor/test/', views.monitor_test, name='monitor_test'),   # <-- requires the view above
#     path('train/', views.train_model, name='train_model'),
#     path('test/', views.test_model, name='test_model'),
#     path('generate/', views.generate_test_data, name='generate_test_data'),
#     path('monitor/test-pattern/', views.test_pattern, name='test_pattern'),  # <- new
#
# ]
# ai_anomaly/urls.py

from django.urls import path
from . import views

app_name = "ai_anomaly"

urlpatterns = [
    # AI Dashboard
    path("dashboard/", views.ai_dashboard, name="dashboard"),

    # AI Actions
    path("dashboard/train/", views.dashboard_train, name="dashboard_train"),
    path("dashboard/detect/", views.dashboard_detect, name="dashboard_detect"),
    path("dashboard/generate/", views.dashboard_generate, name="dashboard_generate"),

    # Manual block / unblock from AI dashboard
    path("dashboard/block/<int:user_id>/", views.block_user, name="block_user"),
    path("dashboard/unblock/<int:user_id>/", views.unblock_user, name="unblock_user"),
]
