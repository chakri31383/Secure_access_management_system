# files/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, JsonResponse, HttpResponseForbidden, Http404
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.conf import settings

from .models import File
from .forms import FileUploadForm, FileEditForm
from .utils import generate_qr   # your existing util
from dashboard.utils import user_has_permission   # adjust import path if different

@login_required
def files_list(request):
    user = request.user
    q = (request.GET.get('q') or '').strip()
    mode = request.GET.get('mode', 'mine')   # mine | org | public
    page = request.GET.get('page', 1)

    qs = File.objects.all()

    if mode == 'org':
        if user.org_id is None:
            qs = File.objects.none()
        else:
            qs = qs.filter(org_id=user.org_id)
    elif mode == 'public':
        qs = qs.filter(is_public=True)
    else:
        qs = qs.filter(owner=user)

    if q:
        qs = qs.filter(
            Q(filename__icontains=q) |
            Q(description__icontains=q) |
            Q(tags__icontains=q) |
            Q(owner__full_name__icontains=q) |
            Q(owner__email__icontains=q)
        )

    qs = qs.order_by('-is_favorite', '-created_at')
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(page)

    return render(request, 'files/list.html', {
        'files_qs': page_obj,
        'q': q,
        'mode': mode,
        'page_obj': page_obj
    })


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            if getattr(request.user, 'org_id', None):
                obj.org_id = request.user.org_id
            obj.save()
            # generate share link + qr
            link = request.build_absolute_uri(settings.MEDIA_URL + obj.file.name)
            qr_path = generate_qr(link, f'file-{obj.id}')
            obj.shared_link = link
            obj.qr_code = qr_path
            obj.save(update_fields=['shared_link','qr_code'])
            messages.success(request, 'File uploaded successfully.')
            return redirect('files:list')
    else:
        form = FileUploadForm()
    return render(request, 'files/upload.html', {'form': form})


@login_required
def download_file(request, file_id):
    f = get_object_or_404(File, pk=file_id)
    viewer = request.user

    # owner can always download
    if f.owner == viewer:
        pass
    else:
        # org files: member + permission
        if f.org_id:
            if viewer.org_id != f.org_id:
                return HttpResponseForbidden("Not authorized")
            if not user_has_permission(viewer, 'can_view'):
                return HttpResponseForbidden("Permission denied")
        else:
            # non-org private files: only owner or public
            if not f.is_public:
                return HttpResponseForbidden("Not authorized")

    try:
        return FileResponse(f.file.open('rb'), as_attachment=True, filename=f.filename)
    except FileNotFoundError:
        raise Http404("File not found")

#
# @login_required
# def edit_file(request, file_id):
#     f = get_object_or_404(File, pk=file_id)
#     user = request.user
#
#     if f.owner != user and not user_has_permission(user, 'can_edit'):
#         messages.error(request, "Not authorized to edit this file.")
#         return redirect('files:list')
#
#     if request.method == 'POST':
#         form = FileEditForm(request.POST, instance=f)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "File updated.")
#             return redirect('files:list')
#     else:
#         form = FileEditForm(instance=f)
#     return render(request, 'files/edit.html', {'form': form, 'file': f})


@login_required
def delete_file(request, file_id):
    f = get_object_or_404(File, pk=file_id)
    user = request.user

    if f.owner != user and not user_has_permission(user, 'can_delete'):
        messages.error(request, "Not authorized to delete this file.")
        return redirect('files:list')

    if request.method == 'POST':
        try:
            f.file.delete(save=False)
        except Exception:
            pass
        f.delete()
        messages.success(request, "File deleted.")
        return redirect('files:list')

    return render(request, 'files/delete.html', {'file': f})


@login_required
@require_POST
def toggle_favorite(request):
    file_id = request.POST.get('file_id')
    if not file_id:
        return JsonResponse({'ok': False, 'error': 'missing file_id'}, status=400)
    f = get_object_or_404(File, pk=file_id)
    viewer = request.user
    # allow owner or org member to mark favorite (adjust policy as needed)
    if f.owner != viewer and (f.org_id and viewer.org_id != f.org_id):
        return JsonResponse({'ok': False, 'error': 'not authorized'}, status=403)
    f.is_favorite = not f.is_favorite
    f.save(update_fields=['is_favorite'])
    return JsonResponse({'ok': True, 'is_favorite': f.is_favorite})


@login_required
def share_file(request, file_id):
    """
    Create or show a shareable public link for a file.
    Simple implementation: generate a random token, save to File.shared_link (or another model).
    """
    f = get_object_or_404(File, pk=file_id)

    # permission: only owner or org admin / main admin can share
    if request.user != f.owner and request.user.role not in ('OrgAdmin', 'MainAdmin'):
        return HttpResponseForbidden("Not authorized to share this file.")

    # If already has a shared_link, show it. Otherwise create a short token URL.
    if not f.shared_link:
        token = uuid.uuid4().hex[:24]
        # Example public URL pattern (you must have a public view to serve this token)
        # You can create a separate view 'public_download' that accepts token and returns file
        f.shared_link = request.build_absolute_uri(f"/files/public/{token}/")
        # Optionally store token in another column; this example reuses shared_link (URL).
        f.save(update_fields=['shared_link'])

    return render(request, 'files/share.html', {'file': f})


@login_required
def edit_file(request, file_id):
    """
    Edit file metadata or replace file. Minimal edit form (title/description).
    """
    f = get_object_or_404(File, pk=file_id)

    # permission to edit
    if request.user != f.owner and request.user.role not in ('OrgAdmin', 'MainAdmin'):
        messages.error(request, "You don't have permission to edit this file.")
        return redirect('files:list')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        new_file = request.FILES.get('file')
        if title:
            f.filename = title
        f.description = description
        if new_file:
            # delete old file if you want
            try:
                f.file.delete(save=False)
            except Exception:
                pass
            f.file = new_file
        f.save()
        messages.success(request, "File updated.")
        return redirect('files:list')

    return render(request, 'files/edit.html', {'file': f})