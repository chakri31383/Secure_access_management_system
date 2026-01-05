# ai_anomaly/views.py
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
#ai_anomaly/views.py
#
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.views.decorators.http import require_POST
# from django.utils.timezone import now, timedelta
#
# from accounts.models import User
# from dashboard.models import ActivityLog
# from .models import UserActivity
# from .detection import train_anomaly_model, predict_anomaly
#
#
# @login_required
# def ai_dashboard(request):
#     if request.user.role != "MainAdmin":
#         messages.error(request, "Access denied.")
#         return redirect("dashboard_home")
#
#     last_24h = now() - timedelta(hours=24)
#     activities = UserActivity.objects.filter(created_at__gte=last_24h)
#
#     total_events = activities.count()
#     total_users = activities.values("user").distinct().count()
#     blocked_users = User.objects.filter(is_blocked=True).count()
#
#     high_risk = []
#     anomalies = 0
#
#     for a in activities:
#         is_anomaly, risk = predict_anomaly(a.feature_vector())
#         if is_anomaly:
#             anomalies += 1
#         if risk > 0.65:
#             high_risk.append({
#                 "user": a.user,  # ✅ FULL USER OBJECT
#                 "downloads": a.downloads,
#                 "files": a.files,
#                 "failed": a.failed_logins,
#                 "risk": risk
#             })
#
#     context = {
#         "total_users": total_users,
#         "total_events": total_events,
#         "anomaly_count": anomalies,
#         "blocked_users": blocked_users,
#         "high_risk": sorted(high_risk, key=lambda x: x["risk"], reverse=True),
#         "recent_logs": ActivityLog.objects.order_by("-timestamp")[:10],
#     }
#
#     return render(request, "ai_anomaly/dashboard.html", context)
#
#
# # ------------------ DASHBOARD ACTIONS ------------------
#
# @login_required
# @require_POST
# def dashboard_train(request):
#     train_anomaly_model(UserActivity.objects.all())
#     messages.success(request, "🤖 AI model trained successfully.")
#     ActivityLog.objects.create(user=request.user, action="AI model trained")
#     return redirect("ai_anomaly:dashboard")
#
#
# @login_required
# @require_POST
# def dashboard_detect(request):
#     if request.user.role != "MainAdmin":
#         messages.error(request, "Access denied.")
#         return redirect("ai_anomaly:dashboard")
#
#     flagged = 0
#     blocked = 0
#
#     activities = UserActivity.objects.select_related("user")
#
#     for a in activities:
#         is_anomaly, risk = predict_anomaly(a.feature_vector())
#
#         if is_anomaly:
#             flagged += 1
#
#             # 🚨 AUTO-BLOCK POLICY
#             if risk >= 0.65 and not a.user.is_blocked:
#                 a.user.is_blocked = True
#                 a.user.save(update_fields=["is_blocked"])
#                 blocked += 1
#
#                 ActivityLog.objects.create(
#                     user=a.user,
#                     action=f"User auto-blocked by AI | Risk={risk}"
#                 )
#
#     messages.success(
#         request,
#         f"Detection complete → {flagged} anomalies, {blocked} users blocked."
#     )
#
#     ActivityLog.objects.create(
#         user=request.user,
#         action=f"AI detection run | {flagged} anomalies | {blocked} blocked"
#     )
#
#     return redirect("ai_anomaly:dashboard")
#
#
#
# @login_required
# @require_POST
# def dashboard_generate(request):
#     patterns = [
#         (5, 5, 0),
#         (45, 3, 0),
#         (2, 50, 0),
#         (1, 1, 55),
#     ]
#
#     for d, f, fl in patterns:
#         UserActivity.objects.create(
#             user=request.user,
#             downloads=d,
#             files=f,
#             failed_logins=fl
#         )
#
#     messages.success(request, "🧪 Test anomaly data generated.")
#     return redirect("ai_anomaly:dashboard")



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.timezone import now, timedelta
from django.db.models import Sum

from accounts.models import User
from dashboard.models import ActivityLog
from .models import UserActivity
from .detection import train_anomaly_model_from_matrix, predict_anomaly


@login_required
def ai_dashboard(request):
    if request.user.role != "MainAdmin":
        messages.error(request, "Access denied.")
        return redirect("dashboard:dashboard_home")

    last_24h = now() - timedelta(hours=24)
    activities = UserActivity.objects.filter(created_at__gte=last_24h)

    total_events = activities.count()
    total_users = activities.values("user").distinct().count()
    blocked_users = User.objects.filter(is_blocked=True).count()

    high_risk = []
    anomalies = 0

    for a in activities.select_related("user"):
        is_anom, risk = predict_anomaly(a.feature_vector())
        if is_anom:
            anomalies += 1
        if risk >= 0.65:
            high_risk.append({
                "user": a.user,
                "downloads": a.downloads,
                "files": a.files,
                "failed": a.failed_logins,
                "risk": risk
            })

    return render(request, "ai_anomaly/dashboard.html", {
        "total_users": total_users,
        "total_events": total_events,
        "anomaly_count": anomalies,
        "blocked_users": blocked_users,
        "high_risk": sorted(high_risk, key=lambda x: x["risk"], reverse=True),
        "recent_logs": ActivityLog.objects.order_by("-timestamp")[:10],
    })


# ---------- TRAIN ----------

def build_training_matrix():
    qs = (
        UserActivity.objects
        .filter(user__role__in=["User", "OrgAdmin"])
        .values("user")
        .annotate(
            downloads=Sum("downloads"),
            files=Sum("files"),
            failed=Sum("failed_logins"),
        )
    )

    X = []
    for r in qs:
        d, f, fl = r["downloads"], r["files"], r["failed"]
        dpf = d / max(f, 1)
        fr = fl / max(d + f, 1)
        X.append([d, f, fl, dpf, fr])

    return X


@login_required
@require_POST
def dashboard_train(request):
    X = build_training_matrix()

    if len(X) < 5:
        messages.error(request, "Not enough distinct users to train AI.")
        return redirect("ai_anomaly:dashboard")

    train_anomaly_model_from_matrix(X)
    ActivityLog.objects.create(user=request.user, action="AI model trained")
    messages.success(request, "🤖 AI model trained successfully.")
    return redirect("ai_anomaly:dashboard")


# ---------- GENERATE DATA ----------

@login_required
@require_POST
def dashboard_generate(request):
    users = User.objects.filter(role__in=["User", "OrgAdmin"], is_blocked=False)

    patterns = [
        (5, 5, 0),
        (45, 3, 0),
        (2, 50, 0),
        (1, 1, 55),
    ]

    for user in users:
        for d, f, fl in patterns:
            UserActivity.objects.create(
                user=user,
                downloads=d,
                files=f,
                failed_logins=fl
            )

    messages.success(request, "🧪 Multi-user AI test data generated.")
    return redirect("ai_anomaly:dashboard")
@login_required
@require_POST
def dashboard_detect(request):
    if request.user.role != "MainAdmin":
        messages.error(request, "Access denied.")
        return redirect("ai_anomaly:dashboard")

    flagged = 0
    blocked = 0

    activities = UserActivity.objects.select_related("user")

    for a in activities:
        is_anomaly, risk = predict_anomaly(a.feature_vector())

        if is_anomaly:
            flagged += 1

            if risk >= 0.65 and not a.user.is_blocked:
                a.user.is_blocked = True
                a.user.save(update_fields=["is_blocked"])
                blocked += 1

                ActivityLog.objects.create(
                    user=a.user,
                    action=f"AI auto-blocked user | Risk={risk}"
                )

    ActivityLog.objects.create(
        user=request.user,
        action=f"AI detection run | {flagged} anomalies | {blocked} blocked"
    )

    messages.success(
        request,
        f"Detection complete → {flagged} anomalies, {blocked} users blocked."
    )

    return redirect("ai_anomaly:dashboard")


from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import User
from dashboard.models import ActivityLog


@login_required
@require_POST
def block_user(request, user_id):
    if request.user.role != "MainAdmin":
        messages.error(request, "Access denied.")
        return redirect("ai_anomaly:dashboard")

    user = get_object_or_404(User, id=user_id)
    user.is_blocked = True
    user.save(update_fields=["is_blocked"])

    ActivityLog.objects.create(
        user=request.user,
        action=f"User {user.email} manually blocked from AI dashboard"
    )

    messages.error(request, f"🚫 {user.email} has been blocked.")
    return redirect("ai_anomaly:dashboard")


@login_required
@require_POST
def unblock_user(request, user_id):
    if request.user.role != "MainAdmin":
        messages.error(request, "Access denied.")
        return redirect("ai_anomaly:dashboard")

    user = get_object_or_404(User, id=user_id)
    user.is_blocked = False
    user.save(update_fields=["is_blocked"])

    ActivityLog.objects.create(
        user=request.user,
        action=f"User {user.email} unblocked from AI dashboard"
    )

    messages.success(request, f"✅ {user.email} has been unblocked.")
    return redirect("ai_anomaly:dashboard")
