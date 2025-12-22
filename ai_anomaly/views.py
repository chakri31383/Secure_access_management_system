# # ai_anomaly/views.py
# import os
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.contrib import messages
# from django.http import JsonResponse, HttpResponseBadRequest
# from django.views.decorators.http import require_POST
#
# # import detection helpers - move detection.py inside ai_anomaly or import with package path
# try:
#     from .detection import train_anomaly_model, load_anomaly_model, predict_anomaly
# except Exception:
#     # fallback if detection.py is at project root (not recommended)
#     from detection import train_anomaly_model, load_anomaly_model, predict_anomaly
#
# # simple permission: allow MainAdmin or OrgAdmin
# def is_admin_user(u):
#     return getattr(u, "role", None) in ("MainAdmin","OrgAdmin")
#
# @login_required
# @user_passes_test(is_admin_user)
# def monitor(request):
#     # load model status
#     model = load_anomaly_model()
#     model_present = model is not None
#     # Example: get some activity stats to show on page (replace with real DB queries)
#     # For demo we will build some synthetic rows; in production fetch aggregated user stats
#     demo_stats = [
#         {"user_id": 1, "email": "alice@example.com", "downloads": 2, "uploads": 0, "failed_logins": 0},
#         {"user_id": 2, "email": "bob@example.com",   "downloads": 50, "uploads": 0, "failed_logins": 0},  # suspicious
#     ]
#     # Use predict_anomaly to mark suspicious rows (if model available)
#     for row in demo_stats:
#         row["anomaly"] = predict_anomaly([row["downloads"], row["uploads"], row["failed_logins"]]) if model_present else False
#
#     context = {
#         "model_present": model_present,
#         "demo_stats": demo_stats,
#     }
#     return render(request, "ai_anomaly/monitor.html", context)
#
#
# @require_POST
# @login_required
# @user_passes_test(is_admin_user)
# def train_model(request):
#     # In real world: collect features from DB -> list of feature vectors [[d,u,fl], ...]
#     # For demo build small dataset (or fetch real user activity table)
#     activities = [
#         [2,1,0],
#         [3,0,0],
#         [1,0,1],
#         [4,1,0],
#         [5,0,0],
#         [40,10,0],  # some high-activity rows to help model learn
#     ]
#     clf = train_anomaly_model(activities)
#     if clf is None:
#         messages.error(request, "Not enough data to train the model (need at least 5 rows).")
#     else:
#         messages.success(request, "Model trained/rebuilt successfully.")
#     return redirect('ai_anomaly:monitor')
#
#
# @login_required
# @user_passes_test(is_admin_user)
# def test_model(request):
#     # simple GET test using query params ?d=..&u=..&f=..
#     try:
#         d = int(request.GET.get('d', 0))
#         u = int(request.GET.get('u', 0))
#         f = int(request.GET.get('f', 0))
#     except ValueError:
#         return HttpResponseBadRequest("Invalid numeric values")
#     is_anom = predict_anomaly([d, u, f])
#     return JsonResponse({"downloads": d, "uploads": u, "failed_logins": f, "is_anomaly": bool(is_anom)})
#
#
# @login_required
# @user_passes_test(is_admin_user)
# def generate_test_data(request):
#     # optional helper to create demo data (could be async)
#     # For demo just redirect back with a message
#     messages.success(request, "Generated test activity (demo).")
#     return redirect('ai_anomaly:monitor')
# # ai_anomaly/views.py  (add this)
# from django.http import JsonResponse
# from django.views.decorators.http import require_GET
# from django.contrib.auth.decorators import login_required, user_passes_test
#
# def is_admin_user(u):
#     return getattr(u, "role", None) in ("MainAdmin", "OrgAdmin")
#
# @login_required
# @user_passes_test(is_admin_user)
# @require_GET
# def monitor_test(request):
#     """
#     Simple GET test endpoint for the monitor page.
#     Returns a tiny JSON payload so the URL can be reversed and visited.
#     """
#     # Example quick demo payload; adapt to return real stats if available.
#     demo = {
#         "ok": True,
#         "msg": "monitor_test endpoint is reachable",
#         "server_time": __import__("datetime").datetime.utcnow().isoformat() + "Z"
#     }
#     return JsonResponse(demo)
# # ai_anomaly/views.py  (add these imports near top if not present)
# from django.shortcuts import render, redirect
# from django.http import JsonResponse, HttpResponse
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.views.decorators.http import require_POST, require_GET
# import traceback
#
# # import your detection helpers (path: /mnt/data/detection.py)
# # ensure ai_anomaly package can import them; if not, use relative or absolute import
# try:
#     from detection import predict_anomaly, load_anomaly_model, train_anomaly_model
# except Exception:
#     # fallback if module path isn't in pythonpath — try relative import
#     try:
#         from .detection import predict_anomaly, load_anomaly_model, train_anomaly_model
#     except Exception:
#         predict_anomaly = None
#         load_anomaly_model = None
#         train_anomaly_model = None
#
# def is_admin_user(u):
#     return getattr(u, "role", None) in ("MainAdmin", "OrgAdmin")
#
# @login_required
# @user_passes_test(is_admin_user)
# @require_POST
# def test_pattern(request):
#     """
#     Trigger a few canned test patterns (POST).
#     Template uses {% url 'ai_anomaly:test_pattern' %} to call this.
#     """
#     # Example patterns: [downloads, files, failed_logins]
#     patterns = [
#         [2,1,0],
#         [3,2,0],
#         [50,0,0],   # clear anomaly
#         [5,5,10],   # suspicious
#     ]
#     results = []
#     try:
#         for p in patterns:
#             if callable(predict_anomaly):
#                 is_anom = predict_anomaly(p)
#             else:
#                 # no model available -> treat as 'not implemented' but return heuristic
#                 is_anom = (p[0] > 20 or p[2] > 5)
#             results.append({'pattern': p, 'anomaly': bool(is_anom)})
#     except Exception as e:
#         return JsonResponse({'ok': False, 'error': str(e), 'trace': traceback.format_exc()}, status=500)
#
#     # If request is AJAX/JS, return JSON; otherwise redirect back with message (simple)
#     if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
#         return JsonResponse({'ok': True, 'results': results})
#     # plain POST from form -> render small page or redirect back
#     return render(request, 'ai_anomaly/test_pattern_results.html', {'results': results})
# ai_anomaly/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from accounts.models import User
from dashboard.models import ActivityLog
from .models import UserActivity
from .detection import train_anomaly_model, predict_anomaly


# -----------------------------
# AI MONITOR DASHBOARD
# -----------------------------
@login_required
def monitor(request):
    """
    Main AI Anomaly Monitor Page
    """
    if request.user.role != "MainAdmin":
        messages.error(request, "Access denied.")
        return redirect("dashboard_home")

    activities = UserActivity.objects.order_by("-created_at")[:50]

    return render(request, "ai_anomaly/monitor.html", {
        "activities": activities
    })


# -----------------------------
# TRAIN MODEL VIEW
# -----------------------------
@login_required
def train_model(request):
    if request.user.role != "MainAdmin":
        messages.error(request, "Access denied.")
        return redirect("ai_anomaly:monitor")

    activities = UserActivity.objects.all()
    model = train_anomaly_model(activities)

    if model:
        messages.success(request, "AI anomaly model trained successfully.")
        ActivityLog.objects.create(
            user=request.user,
            action="AI anomaly model trained"
        )
    else:
        messages.warning(request, "Not enough data to train AI model.")

    return redirect("ai_anomaly:monitor")


# -----------------------------
# DETECT ANOMALY (FROM UI)
# -----------------------------
@login_required
def detect_anomaly(request):
    """
    Called from slider UI
    """
    if request.method != "POST":
        return redirect("ai_anomaly:monitor")

    downloads = int(request.POST.get("downloads", 0))
    files = int(request.POST.get("files", 0))
    failed_logins = int(request.POST.get("failed_logins", 0))

    is_anomaly = predict_anomaly(downloads, files, failed_logins)

    # store activity
    UserActivity.objects.create(
        user=request.user,
        downloads=downloads,
        files=files,
        failed_logins=failed_logins
    )

    if is_anomaly:
        request.user.is_blocked = True
        request.user.save(update_fields=["is_blocked"])

        ActivityLog.objects.create(
            user=request.user,
            action=f"AI anomaly detected → user blocked (D={downloads}, F={files}, FL={failed_logins})"
        )

        messages.error(request, "🚨 Anomaly detected! User has been blocked.")
    else:
        ActivityLog.objects.create(
            user=request.user,
            action=f"Normal behavior (D={downloads}, F={files}, FL={failed_logins})"
        )
        messages.success(request, "✅ Normal behavior detected.")

    return redirect("ai_anomaly:monitor")


# -----------------------------
# AUTO TEST (DEMO PURPOSE)
# -----------------------------
@login_required
def auto_test(request):
    """
    Generates synthetic activity for demo/testing
    """
    if request.user.role != "MainAdmin":
        messages.error(request, "Access denied.")
        return redirect("ai_anomaly:monitor")

    patterns = [
        (5, 2, 0),
        (10, 4, 1),
        (45, 3, 0),
        (2, 50, 0),
        (1, 1, 55),
    ]

    for d, f, fl in patterns:
        UserActivity.objects.create(
            user=request.user,
            downloads=d,
            files=f,
            failed_logins=fl
        )

    messages.success(request, "Synthetic test activity generated.")
    return redirect("ai_anomaly:monitor")
