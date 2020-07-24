import json
import os
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from PIL import Image


class Convert:
    """
    Converts image to different mode
    """

    def __init__(self, mode):
        self.mode = mode

    def process(self, img):
        return img.convert(self.mode)


class Doodle(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='doodles/', null=False)
    processed_image = ImageSpecField(
        source='image',
        processors=[ResizeToFill(400, 300), Convert('1')],
        format='BMP',
        options={'quality': 100},
    )
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    active = models.BooleanField(blank=True, default=False)
    epaper_array = models.TextField(blank=True, default="")

    class Meta:
        get_latest_by = "created_at"

    def to_epaper_format(self):
        return ",".join(self.to_epaper_array())

    def to_epaper_array(self):
        """Image must be converted into a stream of hex values.

        Values are from 0 to 255 where each value have 8 pixels.
        """
        if not self.image:
            return []

        # cache_key = f"doodle_{self.id}"
        stream = json.loads(self.epaper_array) if self.epaper_array else None
        if not stream:
            print("#"*1000)
            im = Image.open(self.processed_image.file)
            im = im.convert("1")
            stream = []
            buf = []
            for y in range(im.size[1]):
                for x in range(im.size[0]):
                    pixel = im.getpixel((x, y))
                    pixel = pixel if pixel == 0 else 1
                    buf.append(pixel)
                    if len(buf) == 8:
                        stream.append(str(int("".join(str(p) for p in buf), 2)))
                        buf = []
            self.epaper_array = json.dumps(stream)
            self.save()
        return stream

    def save(self, *args, **kwargs):
        super().save(*args)
        cleanup()


def cleanup():
    existing_images = []
    existing_processed_images = []
    to_delete = []
    for d in Doodle.objects.all():
        existing_images.append(d.image.file.file.name)
        existing_processed_images.append(d.processed_image.file.file.name)

    for f in os.listdir(os.path.join(settings.MEDIA_ROOT, 'doodles')):
        ff = os.path.join(settings.MEDIA_ROOT, 'doodles', f)
        if ff not in existing_images:
            to_delete.append(ff)

    for f in os.listdir(os.path.join(settings.MEDIA_ROOT, 'CACHE/images/doodles/')):
        ff = os.path.join(settings.MEDIA_ROOT, 'CACHE/images/doodles/', f)
        if os.path.isdir(ff):
            to_delete.append(ff)
            for innerf in os.listdir(ff):
                innerff = os.path.join(ff, innerf)
                if innerff not in existing_processed_images:
                    to_delete.append(innerff)
        else:
            if ff not in existing_processed_images:
                to_delete.append(ff)

    for f in to_delete:
        if not os.path.isdir(f):
            os.remove(f)
    for f in to_delete:
        if os.path.isdir(f):
            try:
                os.rmdir(f)
            except OSError:
                pass
