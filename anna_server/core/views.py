from django.http import HttpResponse
from core.models import Doodle


def index(request):
    doodle = Doodle.objects.order_by("created_at").filter(active=True).last()
    if not doodle:
        return HttpResponse(1)
    return HttpResponse(doodle.created_at.timestamp())


def image(request):
    doodle = Doodle.objects.order_by("created_at").filter(active=True).last()
    return HttpResponse(doodle.to_epaper_format())
