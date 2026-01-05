
from accounts.models import User


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Organization, Role, ActivityLog, JoinRequest  # ensure JoinRequest imported
# other imports...
# dashboard/views.py (snippet)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.conf import settings
from files.models import File
import humanize  # optional; helpful to display sizes
#
# @login_required
# def admin_dashboard(request):
#     user = request.user
#     if user.role != 'MainAdmin':
#         messages.error(request, "Only Main Admin can access this page.")
#         return redirect('dashboard_home')
#
#     # Handle POST actions
#     if request.method == 'POST':
#         # Delete organization
#         if request.POST.get('delete_org_id'):
#             org_id = request.POST.get('delete_org_id')
#             org = get_object_or_404(Organization, pk=org_id)
#             # Optional: delete related files/users carefully (or mark org inactive)
#             org.delete()
#             ActivityLog.objects.create(user=user, action=f"Deleted organization {org.name}")
#             messages.success(request, f"Organization {org.name} deleted.")
#             return redirect('dashboard:admin_dashboard')
#
#         # Block / Unblock user
#         if request.POST.get('block_user_id'):
#             uid = request.POST.get('block_user_id')
#             target = get_object_or_404(User, pk=uid)
#             target.is_blocked = True
#             # optionally remove org membership
#             target.org_id = None
#             target.save(update_fields=['is_blocked','org_id'])
#             ActivityLog.objects.create(user=user, action=f"Blocked user {target.email}")
#             messages.success(request, f"User {target.email} blocked.")
#             return redirect('dashboard:admin_dashboard')
#
#         if request.POST.get('unblock_user_id'):
#             uid = request.POST.get('unblock_user_id')
#             target = get_object_or_404(User, pk=uid)
#             target.is_blocked = False
#             target.save(update_fields=['is_blocked'])
#             ActivityLog.objects.create(user=user, action=f"Unblocked user {target.email}")
#             messages.success(request, f"User {target.email} unblocked.")
#             return redirect('dashboard:admin_dashboard')
#
#     # Stats
#     total_users = User.objects.count()
#     active_users = User.objects.filter(is_active=True, is_blocked=False).count()
#     blocked_users = User.objects.filter(is_blocked=True).count()
#     total_orgs = Organization.objects.count()
#
#     # Files stats (global)
#     total_files = File.objects.count()
#     # storage: sum of size field if you store it; otherwise compute from file.size
#     storage_bytes = File.objects.aggregate(total=Sum('file_size'))['total'] or 0  # requires file_size field
#     storage_total_bytes = settings.MAX_STORAGE_BYTES if hasattr(settings, 'MAX_STORAGE_BYTES') else 1024**3 * 10
#     storage_percent = int(storage_bytes * 100 / max(1, storage_total_bytes))
#
#     # Prepare org list with per-org counts and storage
#     orgs_qs = Organization.objects.all().annotate(
#         files_count=Count('file')  # requires related name 'file' or adjust
#     )
#     # If File model has org_id integer field: use File.objects.filter(org_id=org.id).aggregate(...)
#     orgs = []
#     for o in orgs_qs:
#         # calculate storage per org
#         storage_org = File.objects.filter(org_id=o.id).aggregate(total=Sum('file_size'))['total'] or 0
#         o.human_storage = humanize.naturalsize(storage_org) if storage_org else "0 B"
#         o.files_count = getattr(o, 'files_count', File.objects.filter(org_id=o.id).count())
#         o.storage_pct = int((storage_org * 100)/max(1, storage_total_bytes))
#         orgs.append(o)
#
#     # Users list (for right column)
#     users_qs = User.objects.order_by('-created_at')[:30]
#     users = []
#     for u in users_qs:
#         u.org_name = Organization.objects.filter(id=u.org_id).values_list('name', flat=True).first() if u.org_id else None
#         users.append(u)
#
#     # Recent logs
#     logs = ActivityLog.objects.select_related('user').order_by('-timestamp')[:50]
#
#     context = {
#         'total_users': total_users,
#         'active_users': active_users,
#         'blocked_users': blocked_users,
#         'total_orgs': total_orgs,
#         'recent_orgs_count': Organization.objects.order_by('-created_at')[:5].count(),
#         'total_files': total_files,
#         'public_files': File.objects.filter(shared_link__isnull=False).count(),
#         'private_files': File.objects.filter(shared_link__isnull=True).count(),
#         'human_storage_used': humanize.naturalsize(storage_bytes),
#         'human_storage_total': humanize.naturalsize(storage_total_bytes),
#         'storage_percent': storage_percent,
#         'orgs': orgs,
#         'users': users,
#         'logs': logs,
#         # optional search query echoes
#         'q_org': request.GET.get('q_org',''),
#         'q_user': request.GET.get('q_user',''),
#     }
#     return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def dashboard_home(request):
    user = request.user
    ActivityLog.objects.create(user=user, action="Visited Dashboard")

    # MAIN ADMIN → redirect
    if user.role == "MainAdmin":
        return redirect("dashboard:admin_dashboard")

    # ORG ADMIN
    elif user.role == "OrgAdmin":
        return redirect("dashboard:org_dashboard")

    # NORMAL USER
    else:
        user_org = None
        if user.org_id:
            user_org = Organization.objects.filter(id=user.org_id).first()

        user_requests = JoinRequest.objects.filter(user=user).order_by('-created_at')
        has_pending = user_requests.filter(status='pending').exists()
        can_request_join = (user.org_id is None and not has_pending)

        user_files_qs = File.objects.filter(owner=user).order_by('-created_at')
        user_files_count = user_files_qs.count()
        user_files = list(user_files_qs[:6])

        recent_logs = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:6]

        return render(request, 'dashboard/user_dashboard.html', {
            'user_org': user_org,
            'user_requests': user_requests,
            'has_pending': has_pending,
            'can_request_join': can_request_join,
            'user_files_count': user_files_count,
            'user_files': user_files,
            'recent_logs': recent_logs,
        })



@login_required
def create_org(request):
    user = request.user

    if user.role != "MainAdmin":
        messages.error(request, "Only Main Admin can create organizations.")
        return redirect('dashboard_home')

    # show only users whose org_id is NULL
    available_users = User.objects.filter(org_id__isnull=True)

    if request.method == 'POST':
        name = request.POST.get('name')
        admin_user_id = request.POST.get('admin_user_id')

        if not name:
            messages.error(request, "Organization name is required.")
            return redirect('create_org')

        if not admin_user_id:
            messages.error(request, "Please select an organization admin.")
            return redirect('create_org')

        # get user to assign as org admin
        try:
            admin_user = User.objects.get(id=admin_user_id)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('create_org')

        # extra safety
        if admin_user.org_id is not None:
            messages.error(request, "This user is already linked to an organization.")
            return redirect('create_org')

        # create organization
        org = Organization.objects.create(
            name=name,
            admin=admin_user,
            payment_status="approved"
        )

        # update user table
        admin_user.org_id = org.id
        admin_user.role = "OrgAdmin"
        admin_user.save()

        messages.success(request, f"Organization '{name}' created and {admin_user.full_name} set as Org Admin.")
        return redirect('dashboard_home')

    return render(request, 'dashboard/create_org.html', {
        'users': available_users
    })

@login_required
def assign_role(request):
    user = request.user
    if user.role != "OrgAdmin":
        messages.error(request, "Only Org Admin can assign roles.")
        return redirect('dashboard_home')

    if request.method == 'POST':
        target_email = request.POST['email']
        role_name = request.POST['role']
        try:
            target_user = User.objects.get(email=target_email)
            target_user.role = role_name
            target_user.org_id = user.org_id
            target_user.save()
            messages.success(request, f"Role '{role_name}' assigned to {target_email}.")
            ActivityLog.objects.create(user=user, action=f"Assigned {role_name} to {target_email}")
        except User.DoesNotExist:
            messages.error(request, "User not found.")
    return redirect('dashboard_home')

@login_required
def activity_logs(request):
    logs = ActivityLog.objects.all().order_by('-timestamp')[:50]
    return render(request, 'dashboard/home.html', {'logs': logs})
# dashboard/views.py
# dashboard/views.py (replace org_dashboard)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from .models import RolePermission, JoinRequest, Organization, ActivityLog
from .utils import user_has_permission
@login_required
def org_dashboard(request):
    user = request.user
    if user.role != "OrgAdmin":
        messages.error(request, "Only Org Admin can access this page.")
        return redirect('dashboard_home')

    org_id = user.org_id
    if org_id is None:
        messages.error(request, "You are not associated with an organization.")
        return redirect('dashboard_home')

    students_in_org = User.objects.filter(org_id=org_id).order_by('full_name')
    students_available = User.objects.filter(org_id__isnull=True, is_blocked=False).order_by('full_name')
    roles = RolePermission.objects.filter(org_id=org_id).order_by('-created_at')
    pending_requests = JoinRequest.objects.filter(org_id=org_id, status='pending').select_related('user').order_by('created_at')

    if request.method == 'POST':
        # ---------------- assign role ----------------
        if request.POST.get('assign_role'):
            user_id = request.POST.get('user_id')
            role_name = request.POST.get('role_name', '').strip()
            can_view = request.POST.get('can_view') == '1'
            can_edit = request.POST.get('can_edit') == '1'
            can_delete = request.POST.get('can_delete') == '1'
            can_chat = request.POST.get('can_chat') == '1'
            if not user_id or not role_name:
                messages.error(request, "Please select user and role.")
                return redirect('org_dashboard')
            try:
                with transaction.atomic():
                    target = User.objects.select_for_update().get(pk=user_id)
                    # if they are not yet member, add them to org
                    if target.org_id is None:
                        target.org_id = org_id
                    # ensure not blocked
                    target.is_blocked = False
                    target.role = role_name
                    target.save(update_fields=['org_id','is_blocked','role'])
                    rp, created = RolePermission.objects.update_or_create(
                        name=role_name, org_id=org_id,
                        defaults={'can_view':can_view,'can_edit':can_edit,'can_delete':can_delete,'can_chat':can_chat}
                    )
                    ActivityLog.objects.create(user=user, action=f"Assigned role '{role_name}' to {target.email}")
                messages.success(request, f"Role '{role_name}' assigned to {target.full_name or target.email}.")
            except User.DoesNotExist:
                messages.error(request, "Selected user not found.")
            return redirect('org_dashboard')

        # ---------------- edit (save edited role) ----------------
        if request.POST.get('save_edited_role'):
            role_id = request.POST.get('edit_role_id')
            role_name = request.POST.get('role_name')
            can_view = request.POST.get('can_view') == '1'
            can_edit = request.POST.get('can_edit') == '1'
            can_delete = request.POST.get('can_delete') == '1'
            can_chat = request.POST.get('can_chat') == '1'
            RolePermission.objects.filter(id=role_id, org_id=org_id).update(
                name=role_name, can_view=can_view, can_edit=can_edit, can_delete=can_delete, can_chat=can_chat
            )
            messages.success(request, "Role updated.")
            return redirect('org_dashboard')

        # ---------------- delete role ----------------
        if request.POST.get('delete_role_id'):
            rid = request.POST.get('delete_role_id')
            RolePermission.objects.filter(id=rid, org_id=org_id).delete()
            messages.success(request, "Role deleted.")
            return redirect('org_dashboard')

        # ---------------- block user ----------------
        if request.POST.get('block_user_id'):
            uid = request.POST.get('block_user_id')
            try:
                target = User.objects.get(pk=uid, org_id=org_id)
                target.is_blocked = True
                # remove org membership
                target.org_id = None
                target.role = 'Student'  # reset role or keep previous in separate field
                target.save(update_fields=['is_blocked','org_id','role'])
                ActivityLog.objects.create(user=user, action=f"Blocked user {target.email} from org {org_id}")
                messages.success(request, f"{target.full_name or target.email} blocked.")
            except User.DoesNotExist:
                messages.error(request, "User not found or not in this org.")
            return redirect('org_dashboard')

        # ---------------- unblock user ----------------
        if request.POST.get('unblock_user_id'):
            uid = request.POST.get('unblock_user_id')
            try:
                target = User.objects.get(pk=uid)
                target.is_blocked = False
                # optionally restore org_id if you kept backup, here we re-add to org
                target.org_id = org_id
                target.role = 'Student'
                target.save(update_fields=['is_blocked','org_id','role'])
                ActivityLog.objects.create(user=user, action=f"Unblocked user {target.email} in org {org_id}")
                messages.success(request, f"{target.full_name or target.email} unblocked and re-added to org.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")
            return redirect('org_dashboard')

        # ---------------- review join request (accept/reject) ----------------
        if request.POST.get('review_request_id'):
            req_id = request.POST.get('review_request_id')
            action = request.POST.get('action')
            jr = get_object_or_404(JoinRequest, id=req_id, org_id=org_id)
            if action == 'accept':
                jr.status = 'accepted'; jr.reviewed_at = timezone.now(); jr.reviewed_by = user; jr.save()
                target = jr.user; target.org_id = org_id; target.is_blocked = False; target.role='Student'; target.save(update_fields=['org_id','is_blocked','role'])
                ActivityLog.objects.create(user=user, action=f"Accepted join request: {target.email}")
                messages.success(request, f"{target.full_name or target.email} added to org.")
            else:
                jr.status = 'rejected'; jr.reviewed_at = timezone.now(); jr.reviewed_by = user; jr.save()
                ActivityLog.objects.create(user=user, action=f"Rejected join request: {jr.user.email}")
                messages.info(request, "Request rejected.")
            return redirect('org_dashboard')

    # end POST handling

    return render(request, 'dashboard/org_dashboard.html', {
        'students_in_org': students_in_org,
        'students_available': students_available,
        'roles': roles,
        'pending_requests': pending_requests,
    })
# @login_required
# def org_dashboard(request):
#     user = request.user
#     if user.role != "OrgAdmin":
#         messages.error(request, "Only Org Admin can access this page.")
#         return redirect('dashboard_home')
#
#     org_id = user.org_id
#     if org_id is None:
#         messages.error(request, "You are not associated with an organization.")
#         return redirect('dashboard_home')

    # 1) Users already in this org who are 'Student'
    students_in_org = User.objects.filter(org_id=org_id, role__iexact='student')

    # # 2) Students who are not in any org (available to invite)
    # students_available = User.objects.filter(org_id__isnull=True, role__iexact='student')
    #
    # # 3) Roles/permissions for this org
    # roles = RolePermission.objects.filter(org_id=org_id).order_by('-created_at')
    #
    # # 4) Pending join requests
    # pending_requests = JoinRequest.objects.filter(org_id=org_id, status='pending').select_related('user').order_by('created_at')
    #
    # # ---------- Handle POST actions ----------
    # if request.method == 'POST':
    #     # ASSIGN ROLE / SAVE PERMISSIONS
    #     if request.POST.get('assign_role'):
    #         user_id = request.POST.get('user_id')
    #         role_name = request.POST.get('role_name', '').strip()
    #         can_view = request.POST.get('can_view') == '1'
    #         can_edit = request.POST.get('can_edit') == '1'
    #         can_delete = request.POST.get('can_delete') == '1'
    #         can_chat = request.POST.get('can_chat') == '1'
    #
    #         if not user_id or not role_name:
    #             messages.error(request, "Please select a user and a role name.")
    #             return redirect('org_dashboard')
    #
    #         try:
    #             with transaction.atomic():
    #                 target = User.objects.select_for_update().get(pk=user_id)
    #                 # If target not in org, optionally join them immediately (comment if you want admin to invite only)
    #                 if target.org_id is None:
    #                     target.org_id = org_id
    #
    #                 rp, created = RolePermission.objects.update_or_create(
    #                     name=role_name,
    #                     org_id=org_id,
    #                     defaults={
    #                         'can_view': can_view,
    #                         'can_edit': can_edit,
    #                         'can_delete': can_delete,
    #                         'can_chat': can_chat
    #                     }
    #                 )
    #
    #                 target.role = role_name
    #                 target.save(update_fields=['role', 'org_id'])
    #                 ActivityLog.objects.create(user=user, action=f"Assigned role '{role_name}' to {target.email} (rp {'created' if created else 'updated'})")
    #             messages.success(request, f"Assigned role '{role_name}' to {target.full_name or target.email}.")
    #         except User.DoesNotExist:
    #             messages.error(request, "Selected user not found.")
    #         return redirect('org_dashboard')
    #
    #     # DELETE ROLE
    #     if request.POST.get('delete_role_id'):
    #         role_id = request.POST.get('delete_role_id')
    #         RolePermission.objects.filter(id=role_id, org_id=org_id).delete()
    #         messages.success(request, "Role deleted successfully.")
    #         return redirect('org_dashboard')
    #
    #     # REVIEW JOIN REQUEST
    #     if request.POST.get('review_request_id'):
    #         req_id = request.POST.get('review_request_id')
    #         action = request.POST.get('action')
    #         try:
    #             jr = JoinRequest.objects.get(id=req_id, org_id=org_id)
    #         except JoinRequest.DoesNotExist:
    #             messages.error(request, "Join request not found.")
    #             return redirect('org_dashboard')
    #
    #         if action == 'accept':
    #             jr.status = 'accepted'
    #             jr.reviewed_at = timezone.now()
    #             jr.reviewed_by = user
    #             jr.save(update_fields=['status', 'reviewed_at', 'reviewed_by'])
    #
    #             target = jr.user
    #             target.org_id = org_id
    #             target.role = 'Student'
    #             target.save(update_fields=['org_id', 'role'])
    #             ActivityLog.objects.create(user=user, action=f"Accepted join request: {target.email} -> {jr.org.name}")
    #             messages.success(request, f"{target.full_name or target.email} has been added to the organization.")
    #         else:
    #             jr.status = 'rejected'
    #             jr.reviewed_at = timezone.now()
    #             jr.reviewed_by = user
    #             jr.save(update_fields=['status', 'reviewed_at', 'reviewed_by'])
    #             ActivityLog.objects.create(user=user, action=f"Rejected join request: {jr.user.email} -> {jr.org.name}")
    #             messages.info(request, "Request rejected.")
    #         return redirect('org_dashboard')
    #
    # # GET: render page
    # return render(request, 'dashboard/org_dashboard.html', {
    #     'students_in_org': students_in_org,
    #     'students_available': students_available,
    #     'roles': roles,
    #     'pending_requests': pending_requests,
    # })
from django.http import FileResponse, HttpResponseForbidden, Http404
from django.db import transaction

from files.models import File

from .utils import user_has_permission

@login_required
def list_files(request, student_id=None):
    """
    If student_id provided -> student mode (files for a specific student).
    Otherwise -> org mode (all files in the organization) or user's own files.
    """
    viewer = request.user
    if viewer.org_id is None:
        messages.error(request, "You are not assigned to any organization.")
        return redirect('dashboard_home')

    # Student mode
    if student_id:
        target = get_object_or_404(User, pk=student_id)
        if target.org_id != viewer.org_id:
            messages.error(request, "Student not in your organization.")
            return redirect('dashboard_home')
        if not user_has_permission(viewer, 'can_view'):
            messages.error(request, "You don't have permission to view this student's files.")
            return redirect('dashboard_home')
        files_qs = File.objects.filter(owner=target).order_by('-created_at')
        title = f"Files for {target.full_name}"

    else:
        mode = request.GET.get('mode', 'org')
        if mode == 'org':
            if not user_has_permission(viewer, 'can_view'):
                messages.error(request, "You don't have permission to view organization files.")
                return redirect('dashboard_home')
            files_qs = File.objects.filter(org_id=viewer.org_id).order_by('-created_at')
            title = "Organization Files"
        else:
            # default to current user's files
            files_qs = File.objects.filter(owner=viewer).order_by('-created_at')
            title = "Your Files"

    # Determine viewer permissions (for template buttons)
    can_edit = user_has_permission(viewer, 'can_edit')
    can_delete = user_has_permission(viewer, 'can_delete')
    can_chat = user_has_permission(viewer, 'can_chat')

    return render(request, 'dashboard/list_files.html', {
        'files_qs': files_qs,
        'title': title,
        'can_edit': can_edit,
        'can_delete': can_delete,
        'can_chat': can_chat,
        'viewer': viewer,
    })


@login_required
def edit_file(request, file_id):
    """
    Edit file metadata (title/filename/description). Permission: can_edit.
    The actual file replacement (upload) can be supported as well if desired.
    """
    viewer = request.user
    f = get_object_or_404(File, pk=file_id)

    # same organization?
    if f.org_id != viewer.org_id:
        messages.error(request, "Not authorized.")
        return redirect('list_files')

    if not user_has_permission(viewer, 'can_edit'):
        messages.error(request, "You don't have permission to edit files.")
        return redirect('list_files')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        # optional: allow file replacement
        new_file = request.FILES.get('file')
        if title:
            f.filename = title
        if new_file:
            f.file.delete(save=False)  # delete old file
            f.file = new_file
        f.save()
        messages.success(request, "File updated.")
        return redirect('list_files')

    return render(request, 'dashboard/edit_file.html', {'file': f})


@login_required
def delete_file(request, file_id):
    viewer = request.user
    f = get_object_or_404(File, pk=file_id)

    if f.org_id != viewer.org_id:
        messages.error(request, "Not authorized.")
        return redirect('list_files')

    if not user_has_permission(viewer, 'can_delete'):
        messages.error(request, "You don't have permission to delete files.")
        return redirect('list_files')

    if request.method == 'POST':
        # delete stored file from disk and DB row
        try:
            f.file.delete(save=False)
        except Exception:
            pass
        f.delete()
        messages.success(request, "File deleted.")
        return redirect('list_files')

    # optional confirmation page
    return render(request, 'dashboard/confirm_delete.html', {'file': f})


@login_required
def download_file(request, file_id):
    """
    Secure download / preview view: checks permissions before serving the file.
    For production: prefer serving via authenticated S3 or X-Accel/X-Sendfile.
    """
    viewer = request.user
    f = get_object_or_404(File, pk=file_id)

    if f.org_id != viewer.org_id:
        return HttpResponseForbidden("Not authorized.")

    if not user_has_permission(viewer, 'can_view'):
        return HttpResponseForbidden("Permission denied.")

    # local filesystem file serving (development)
    try:
        response = FileResponse(f.file.open('rb'), as_attachment=True, filename=f.filename)
        return response
    except FileNotFoundError:
        raise Http404("File not found.")
# dashboard/views.py  (append)
from django.utils import timezone
#from django.db import transaction
#from django.shortcuts import render, get_object_or_404


@login_required
def join_org_view(request):
    """
    Page where a user without org can see organizations and request to join.
    If a pending request exists, show 'Pending' instead of create button.
    """
    user = request.user
    if user.org_id is not None:
        messages.info(request, "You are already a member of an organization.")
        return redirect('dashboard_home')

    # list available organizations
    orgs = Organization.objects.all().order_by('name')

    if request.method == 'POST':
        org_id = request.POST.get('org_id')
        message = request.POST.get('message', '').strip()
        org = get_object_or_404(Organization, pk=org_id)

        # check if request already exists
        existing = JoinRequest.objects.filter(user=user, org=org).first()
        if existing:
            if existing.status == 'pending':
                messages.info(request, "You already have a pending request for this organization.")
            elif existing.status == 'accepted':
                messages.info(request, "You are already accepted to this organization.")
            else:
                messages.info(request, "Previous request was rejected. You can create a new one.")
                # optionally allow re-create: create new request
                JoinRequest.objects.create(user=user, org=org, message=message)
                messages.success(request, "Join request submitted.")
                ActivityLog.objects.create(user=user, action=f"Requested to join org {org.name}")
        else:
            JoinRequest.objects.create(user=user, org=org, message=message)
            messages.success(request, "Join request submitted.")
            ActivityLog.objects.create(user=user, action=f"Requested to join org {org.name}")

        return redirect('dashboard_home')

    # GET
    # Also include user's existing requests to show pending status
    user_requests = JoinRequest.objects.filter(user=user).select_related('org').order_by('-created_at')
    return render(request, 'dashboard/join_org.html', {
        'orgs': orgs,
        'user_requests': user_requests,
    })


@login_required
def leave_org_view(request):
    """
    Allow user to leave the organization. Optionally ask for confirmation in template.
    """
    user = request.user
    if user.org_id is None:
        messages.info(request, "You are not a member of any organization.")
        return redirect('dashboard_home')

    if request.method == 'POST':
        old_org = user.org_id
        # clear org membership (keep role or set default)
        user.org_id = None
        # optionally reset role to default Student
        user.role = 'Student'
        user.save(update_fields=['org_id', 'role'])
        ActivityLog.objects.create(user=user, action=f"Left organization id {old_org}")
        messages.success(request, "You have left the organization.")
        return redirect('dashboard_home')

    # GET - show confirm leave page
    org = Organization.objects.filter(pk=user.org_id).first()
    return render(request, 'dashboard/confirm_leave.html', {'org': org})


@login_required
def view_join_requests(request):
    """
    OrgAdmin view: list pending requests for their organization only.
    """
    user = request.user
    if user.role != 'OrgAdmin':
        messages.error(request, "Only Org Admins can review join requests.")
        return redirect('dashboard_home')

    org_id = user.org_id
    if org_id is None:
        messages.error(request, "You are not associated with an organization.")
        return redirect('dashboard_home')

    pending = JoinRequest.objects.filter(org__id=org_id, status='pending').select_related('user', 'org').order_by('created_at')
    return render(request, 'dashboard/pending_requests.html', {'pending': pending})


@login_required
def review_join_request(request, req_id):
    """
    OrgAdmin accepts or rejects a join request.
    POST params:
        action = 'accept' | 'reject'
    """
    user = request.user
    if user.role != 'OrgAdmin':
        messages.error(request, "Only Org Admins can review join requests.")
        return redirect('dashboard_home')

    jr = get_object_or_404(JoinRequest, pk=req_id)
    if jr.org.id != user.org_id:
        messages.error(request, "Not authorized to review this request.")
        return redirect('dashboard_home')

    if request.method == 'POST':
        action = request.POST.get('action')
        reviewer = user
        with transaction.atomic():
            if action == 'accept':
                jr.status = 'accepted'
                jr.reviewed_at = timezone.now()
                jr.reviewed_by = reviewer
                jr.save(update_fields=['status', 'reviewed_at', 'reviewed_by'])

                # set user's org_id and role (use desired default role, e.g. 'Student')
                target = jr.user
                target.org_id = jr.org.id
                # optionally set default role, e.g. 'Student'
                target.role = 'Student'
                target.save(update_fields=['org_id', 'role'])

                ActivityLog.objects.create(user=reviewer, action=f"Accepted join request: {target.email} -> {jr.org.name}")
                messages.success(request, f"{target.full_name} has been added to the organization.")
            else:
                jr.status = 'rejected'
                jr.reviewed_at = timezone.now()
                jr.reviewed_by = reviewer
                jr.save(update_fields=['status', 'reviewed_at', 'reviewed_by'])
                ActivityLog.objects.create(user=reviewer, action=f"Rejected join request: {jr.user.email} -> {jr.org.name}")
                messages.success(request, "Request rejected.")
    return redirect('view_join_requests')
# -----------------------
# ORG DETAIL VIEW
# -----------------------
from django.shortcuts import get_object_or_404
from files.models import File


# -----------------------
# DELETE ORG VIEW
# -----------------------
@login_required
def delete_org(request, org_id):
    user = request.user
    if user.role != "MainAdmin":
        messages.error(request, "Only Main Admin can delete organizations.")
        return redirect('dashboard:dashboard_home')

    org = get_object_or_404(Organization, pk=org_id)

    if request.method == "POST":
        org_name = org.name
        org.delete()
        ActivityLog.objects.create(user=user, action=f"Deleted org {org_name}")
        messages.success(request, f"Organization '{org_name}' deleted.")
        return redirect('dashboard:admin_dashboard')

    return render(request, "dashboard/confirm_org_delete.html", {
        "org": org,
    })
@login_required
def admin_dashboard(request):
    user = request.user
    if user.role != "MainAdmin":
        messages.error(request, "Only Main Admin can access this page.")
        return redirect('dashboard:dashboard_home')

    # Handle POST actions: delete org, block/unblock users
    if request.method == 'POST':
        # Delete organization (MainAdmin only)
        delete_org_id = request.POST.get('delete_org_id')
        if delete_org_id:
            try:
                org = get_object_or_404(Organization, pk=delete_org_id)
                org_name = org.name
                org.delete()  # careful in prod: you may want soft-delete
                ActivityLog.objects.create(user=user, action=f"Deleted organization {org_name}")
                messages.success(request, f"Organization '{org_name}' deleted.")
            except Exception as e:
                messages.error(request, f"Could not delete organization: {e}")
            return redirect('dashboard:admin_dashboard')

        # Block user
        block_user_id = request.POST.get('block_user_id')
        if block_user_id:
            target = get_object_or_404(User, pk=block_user_id)
            target.is_blocked = True
            # remove org membership when blocking (your requirement)
            target.org_id = None
            target.save(update_fields=['is_blocked', 'org_id'])
            ActivityLog.objects.create(user=user, action=f"Blocked user {target.email}")
            messages.success(request, f"{target.email} blocked.")
            return redirect('dashboard:admin_dashboard')

        # Unblock user
        unblock_user_id = request.POST.get('unblock_user_id')
        if unblock_user_id:
            target = get_object_or_404(User, pk=unblock_user_id)
            target.is_blocked = False
            target.save(update_fields=['is_blocked'])
            ActivityLog.objects.create(user=user, action=f"Unblocked user {target.email}")
            messages.success(request, f"{target.email} unblocked.")
            return redirect('dashboard:admin_dashboard')

    # ============= gather stats =============
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True, is_blocked=False).count()
    blocked_users = User.objects.filter(is_blocked=True).count()
    total_orgs = Organization.objects.count()

    total_files = File.objects.count()
    # IMPORTANT: use 'filesize' (your model field)
    storage_bytes = File.objects.aggregate(total=Sum('filesize'))['total'] or 0
    storage_total_bytes = getattr(settings, 'MAX_STORAGE_BYTES', 1024**3 * 10)  # default 10 GB
    storage_percent = int(storage_bytes * 100 / max(1, storage_total_bytes))

    # Build org list with counts and storage info
    orgs_qs = Organization.objects.all().order_by('-created_at')
    orgs = []
    for o in orgs_qs:
        files_count = File.objects.filter(org_id=o.id).count()
        storage_org = File.objects.filter(org_id=o.id).aggregate(total=Sum('filesize'))['total'] or 0
        o.files_count = files_count
        o.human_storage = humanize.naturalsize(storage_org) if storage_org else "0 B"
        o.storage_pct = int(storage_org * 100 / max(1, storage_total_bytes))
        # optionally fetch admin email
        o.admin_email = o.admin.email if getattr(o, 'admin', None) else None
        orgs.append(o)

    # Recent activity logs
    logs = ActivityLog.objects.select_related('user').order_by('-timestamp')[:50]

    # Recent users (for quick view)
    recent_users = User.objects.order_by('-created_at')[:30]
    for u in recent_users:
        u.org_name = Organization.objects.filter(pk=u.org_id).values_list('name', flat=True).first() if u.org_id else None

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'blocked_users': blocked_users,
        'total_orgs': total_orgs,
        'total_files': total_files,
        'human_storage_used': humanize.naturalsize(storage_bytes),
        'human_storage_total': humanize.naturalsize(storage_total_bytes),
        'storage_percent': storage_percent,
        'orgs': orgs,
        'logs': logs,
        'users': recent_users,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

#
# # -----------------------
# # Organization detail (viewed by MainAdmin or OrgAdmin)
# # -----------------------
# @login_required
# def org_detail(request, org_id):
#     # allow both MainAdmin and OrgAdmin of the same org
#     user = request.user
#     org = get_object_or_404(Organization, pk=org_id)
#
#     if user.role != 'MainAdmin' and not (user.role == 'OrgAdmin' and user.org_id == org_id):
#         messages.error(request, "Not authorized to view this organization.")
#         return redirect('dashboard:dashboard_home')
#
#     # files and members
#     files_qs = File.objects.filter(org_id=org_id)
#     files_count = files_qs.count()
#     storage_bytes = files_qs.aggregate(total=Sum('filesize'))['total'] or 0
#     human_storage = humanize.naturalsize(storage_bytes) if storage_bytes else "0 B"
#
#     members = User.objects.filter(org_id=org_id).order_by('full_name')
#
#     # allow main admin to delete org from here (POST)
#     if request.method == 'POST' and request.POST.get('delete_org_id'):
#         if user.role != 'MainAdmin':
#             messages.error(request, "Only Main Admin can delete organization.")
#             return redirect('dashboard:org_detail', org_id=org_id)
#         try:
#             org_name = org.name
#             org.delete()
#             ActivityLog.objects.create(user=user, action=f"Deleted organization {org_name}")
#             messages.success(request, "Organization deleted.")
#             return redirect('dashboard:admin_dashboard')
#         except Exception as e:
#             messages.error(request, f"Error deleting organization: {e}")
#             return redirect('dashboard:org_detail', org_id=org_id)
#
#     context = {
#         'org': org,
#         'files_count': files_count,
#         'human_storage': human_storage,
#         'members': members,
#     }
#     return render(request, 'dashboard/org_detail.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.urls import reverse

from accounts.models import User
from .models import Organization, ActivityLog, JoinRequest
from files.models import File

@login_required
def org_detail(request, org_id):
    """
    View organization details.
    - MainAdmin: can view any org and can delete org.
    - OrgAdmin: can view org only if they belong to it (user.org_id == org_id).
    """

    user = request.user

    # permission: MainAdmin can view any org; OrgAdmin only their org
    if user.role != "MainAdmin" and not (user.role == "OrgAdmin" and user.org_id == org_id):
        messages.error(request, "You are not authorized to view this organization.")
        return redirect('dashboard_home')

    org = get_object_or_404(Organization, pk=org_id)

    # POST actions (delete org) — only MainAdmin allowed
    if request.method == "POST":
        if request.POST.get('delete_org') and user.role == "MainAdmin":
            org_name = org.name
            org.delete()
            ActivityLog.objects.create(user=user, action=f"Deleted organization {org_name} (id={org_id})")
            messages.success(request, f"Organization '{org_name}' deleted.")
            # Redirect to admin dashboard or dashboard home
            try:
                return redirect(reverse('dashboard:admin_dashboard'))
            except Exception:
                return redirect('dashboard_home')

        # fallback: other POST actions could be handled here

    # Members (include blocked flag so you can show blocked/unblocked)
    members_qs = User.objects.filter(org_id=org_id).order_by('full_name')  # includes OrgAdmin(s) and other roles

    # counts
    members_count = members_qs.count()
    blocked_count = members_qs.filter(is_blocked=True).count()

    # Files in organization
    files_qs = File.objects.filter(org_id=org_id).order_by('-created_at')

    files_count = files_qs.count()

    # total storage — aggregate on your actual filesize field name; your model has 'filesize'
    total_bytes = files_qs.aggregate(total=Sum('filesize'))['total'] or 0

    # human-readable size: don't require extra package; simple helper
    def human_size(n):
        # n in bytes
        for unit in ['B','KB','MB','GB','TB']:
            if n < 1024:
                return f"{n:.0f} {unit}" if unit=='B' else f"{n:.1f} {unit}"
            n /= 1024.0
        return f"{n:.1f} PB"

    context = {
        'org': org,
        'members': members_qs,
        'members_count': members_count,
        'blocked_count': blocked_count,
        'files': files_qs,
        'files_count': files_count,
        'total_storage_bytes': total_bytes,
        'total_storage_human': human_size(total_bytes),
        # small helpers for template
        'is_main_admin': user.role == "MainAdmin",
        'is_org_admin': user.role == "OrgAdmin" and user.org_id == org_id,
    }

    return render(request, 'dashboard/org_detail.html', context)
# from django.views.decorators.http import require_POST
# from django.shortcuts import get_object_or_404, redirect
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
#
# from accounts.models import User
# from dashboard.models import ActivityLog


# @login_required
# @require_POST
# def disable_user(request, user_id):
#     # Permission check
#     if request.user.role.lower() != "MainAdmin":
#         messages.error(request, "Access denied.")
#         return redirect("dashboard:admin_dashboard")
#
#     target = get_object_or_404(User, id=user_id)
#
#     if target.is_blocked:
#         messages.info(request, "User is already blocked.")
#         return redirect("dashboard:admin_dashboard")
#
#     target.is_blocked = True
#     target.save(update_fields=["is_blocked"])
#
#     ActivityLog.objects.create(
#         user=request.user,
#         action=f"Disabled user {target.email}"
#     )
#
#     messages.success(request, f"🚫 {target.email} has been blocked.")
#     return redirect("dashboard:admin_dashboard")
#
#
# @login_required
# @require_POST
# def enable_user(request, user_id):
#     if request.user.role.lower() != "MainAdmin":
#         messages.error(request, "Access denied.")
#         return redirect("dashboard:admin_dashboard")
#
#     target = get_object_or_404(User, id=user_id)
#
#     if not target.is_blocked:
#         messages.info(request, "User is already active.")
#         return redirect("dashboard:admin_dashboard")
#
#     target.is_blocked = False
#     target.save(update_fields=["is_blocked"])
#
#     ActivityLog.objects.create(
#         user=request.user,
#         action=f"Enabled user {target.email}"
#     )
#
#     messages.success(request, f"✅ {target.email} has been unblocked.")
#     return redirect("dashboard:admin_dashboard")
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from accounts.models import User

def is_main_admin(user):
    return user.is_authenticated and user.role == "MainAdmin"

@login_required
@user_passes_test(is_main_admin)
@require_POST
def toggle_user_block(request, user_id):
    print("🔥 TOGGLE VIEW HIT 🔥", user_id)

    user = get_object_or_404(User, id=user_id)

    # Prevent admin blocking themselves
    if user == request.user:
        return redirect(request.META.get("HTTP_REFERER", "/"))

    user.is_blocked = not user.is_blocked
    user.save(update_fields=["is_blocked"])

    return redirect(request.META.get("HTTP_REFERER", "/"))
