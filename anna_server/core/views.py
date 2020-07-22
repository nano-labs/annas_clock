from base64 import b64decode
from datetime import datetime
import io

from PIL import Image

from django.contrib.auth.decorators import user_passes_test
from django.core.files.base import File
from django.http import HttpResponse
from django.shortcuts import render
from core.models import Doodle

def index(request):
    doodle = Doodle.objects.order_by("created_at").filter(active=True).last()
    if not doodle:
        return HttpResponse(1)
    return HttpResponse(int(doodle.created_at.timestamp()))


def image(request, line):
    doodle = Doodle.objects.order_by("created_at").filter(active=True).last()
    start = line * 600
    end = (start + 600) + 1
    return HttpResponse(",".join(doodle.to_epaper_array()[start:end]))


@user_passes_test(lambda user: user.is_superuser)
def draw(request):
    if request.method == "POST":
        image = b64decode(request.POST["imgBase64"].replace("data:image/png;base64,", ""))
        im = Image.open(io.BytesIO(image))
        im = im.transpose(Image.ROTATE_90).rotate(180)
        fp = io.BytesIO()
        im.save(fp, "png")
        data = File(fp, name="{}.png".format(datetime.now().strftime("%Y%m%d_%H%M%S")))
        doodle = Doodle.objects.create(owner=request.user, image=data, active=True)
        return HttpResponse(doodle.id)

    return render(request, 'drawing.html', {})
