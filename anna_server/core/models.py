from django.db import models
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
        return stream
