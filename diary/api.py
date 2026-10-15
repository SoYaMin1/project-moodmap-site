from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .stats import get_stats


@login_required
def stats_api(request):
    period = request.GET.get("period", "all")
    if period not in ("week", "month", "year", "all"):
        period = "all"
    return JsonResponse(get_stats(request.user, period))