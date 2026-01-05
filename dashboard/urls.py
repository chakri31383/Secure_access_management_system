# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),            # /dashboard/
    path('admin/', views.admin_dashboard, name='admin_dashboard'),    # /dashboard/admin/
    path('create_org/', views.create_org, name='create_org'),
    path('org/<int:org_id>/', views.org_detail, name='org_detail'),
    path('org/<int:org_id>/delete/', views.delete_org, name='delete_org'),

    # org admin dashboard
    path('org-dashboard/', views.org_dashboard, name='org_dashboard'),

    # join/leave requests
    path('join/', views.join_org_view, name='join_org'),
    path('leave/', views.leave_org_view, name='leave_org'),
    path('requests/', views.view_join_requests, name='view_join_requests'),
    path('requests/<int:req_id>/review/', views.review_join_request, name='review_join_request'),

    # files / file actions (if managed from dashboard)
    path('files/', views.list_files, name='list_files'),
    path('files/<int:file_id>/edit/', views.edit_file, name='edit_file'),
    path('files/<int:file_id>/delete/', views.delete_file, name='delete_file'),
    path('files/<int:file_id>/download/', views.download_file, name='download_file'),
    # path("user/<int:user_id>/disable/", views.disable_user, name="disable_user"),
    # path("user/<int:user_id>/enable/", views.enable_user, name="enable_user"),
    path("user/<int:user_id>/toggle-block/", views.toggle_user_block, name="toggle_user_block"),
]
