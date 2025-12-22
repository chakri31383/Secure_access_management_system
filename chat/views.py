# chat/views.py  (update)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ChatMessage, ChatPermission
from accounts.models import User
from django.db.models import Q

@login_required
def chat_room(request):
    # permission check (as you had)
    # allowed = ChatPermission.objects.filter(user=request.user, approved=True).exists()
    # if not allowed:
    #     return render(request, 'chat/no_access.html')

    # org id of current user (may be null)
    org_id = request.user.org_id

    # build recipients list: for an org-scoped chat, show only org members plus MainAdmin option
    recipients = User.objects.filter(org_id=org_id).exclude(id=request.user.id) if org_id else User.objects.exclude(id=request.user.id)

    # handle POST (send message)
    if request.method == 'POST':
        receiver_val = request.POST.get('receiver')  # can be 'all', 'mainadmin', or a user id
        text = request.POST.get('message', '').strip()
        if not text:
            messages.error(request, "Message cannot be empty.")
            return redirect('chat:chat_room')

        if receiver_val == 'all':
            # broadcast to organization
            ChatMessage.objects.create(sender=request.user, receiver=None, org_id=org_id, message=text)
            messages.success(request, "Broadcast message sent to organization.")
        elif receiver_val == 'mainadmin':
            # OrgAdmin -> MainAdmin channel
            # you may want to select a specific MainAdmin user row; here we mark message as is_to_mainadmin=True
            ChatMessage.objects.create(sender=request.user, receiver=None, org_id=org_id, is_to_mainadmin=True, message=text)
            messages.success(request, "Message sent to Main Admin(s).")
        else:
            # direct message to user id
            try:
                target = User.objects.get(pk=int(receiver_val))
                ChatMessage.objects.create(sender=request.user, receiver=target, org_id=org_id, message=text)
                messages.success(request, f"Message sent to {target.full_name}.")
            except (ValueError, User.DoesNotExist):
                messages.error(request, "Invalid recipient.")

        return redirect('chat:chat_room')

    # GET: fetch messages visible to this user:
    # 1) DMs where user is sender or receiver
    # 2) Broadcasts for user's org (receiver is null, org_id == user's org)
    # 3) If OrgAdmin and reading mainadmin thread: show is_to_mainadmin messages to/from mainadmin(s)
    # 4) If MainAdmin: show is_to_mainadmin messages from orgadmins (and optionally reply)

    base_q = Q(sender=request.user) | Q(receiver=request.user)

    org_broadcast_q = Q(receiver__isnull=True, org_id=org_id) if org_id else Q(pk__isnull=True)  # no org -> no broadcasts
    mainadmin_q = Q(is_to_mainadmin=True, org_id=org_id) if org_id else Q(pk__isnull=True)

    # If current user is MainAdmin, show all is_to_mainadmin messages across orgs
    if request.user.role == 'MainAdmin':
        mainadmin_q = Q(is_to_mainadmin=True)

    msgs = ChatMessage.objects.filter(base_q | org_broadcast_q | mainadmin_q).select_related('sender', 'receiver').order_by('timestamp')

    return render(request, 'chat/chat_room.html', {
        'users': recipients,
        'msgs': msgs,
        'org_id': org_id,
    })
