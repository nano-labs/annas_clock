from datetime import datetime

from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import render
from core.models import Doodle

from base64 import b64decode


def index(request):
    doodle = Doodle.objects.order_by("created_at").filter(active=True).last()
    if not doodle:
        return HttpResponse(1)
    return HttpResponse(int(doodle.created_at.timestamp()))


def image(request, line):
    doodle = Doodle.objects.order_by("created_at").filter(active=True).last()
    start = line * 300
    end = (start + 300) + 1
    return HttpResponse(",".join(doodle.to_epaper_array()[start:end]))


def draw(request):
    if request.method == "POST":
        print(request.POST["imgBase64"].replace("data:image/png;base64,", ""))
        image = b64decode(request.POST["imgBase64"].replace("data:image/png;base64,", ""))
        data = ContentFile(image, name="{}.png".format(datetime.now().strftime("%Y%m%d_%H%M%S")))
        Doodle.objects.create(owner=request.user, image=data, active=True)

    return render(request, 'drawing.html', {})
    # return HttpResponse(",".join(doodle.to_epaper_array()[start:end]))
