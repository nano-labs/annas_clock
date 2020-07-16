from django.contrib import admin
from imagekit.admin import AdminThumbnail
from core.models import Doodle


class DoodleAdmin(admin.ModelAdmin):

    list_display = ("created_at", "admin_thumbnail", "active", "owner")
    admin_thumbnail = AdminThumbnail(image_field='processed_image')
    readonly_fields = ('epaper_format',)
    list_editable = ["active"]

    def epaper_format(self, obj):
        return obj.to_epaper_format()


admin.site.register(Doodle, DoodleAdmin)
