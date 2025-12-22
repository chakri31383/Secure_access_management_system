# ai_anomaly/urls.py
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
from django.urls import path
from . import views

app_name = "ai_anomaly"

urlpatterns = [
    path("monitor/", views.monitor, name="monitor"),
    path("train/", views.train_model, name="train_model"),
    path("detect/", views.detect_anomaly, name="detect_anomaly"),
    path("auto-test/", views.auto_test, name="auto_test"),
]
