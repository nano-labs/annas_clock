from django.http import HttpResponse
from core.models import Doodle


def index(request):
    # from datetime import datetime

    # return HttpResponse(int(datetime.now().timestamp()))

    doodle = Doodle.objects.order_by("created_at").filter(active=True).last()
    if not doodle:
        return HttpResponse(1)
    return HttpResponse(int(doodle.created_at.timestamp()))


def image(request, line):
    doodle = Doodle.objects.order_by("created_at").filter(active=True).last()
    start = line * 300
    end = (start + 300) + 1
    return HttpResponse(",".join(doodle.to_epaper_array()[start:end]))
