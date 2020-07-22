from django.contrib import admin
from django.contrib.auth.models import User
from imagekit.admin import AdminThumbnail
from core.models import Doodle

from django.utils.safestring import mark_safe
from django.contrib.admin import AdminSite


class MyAdminSite(AdminSite):
    site_header = 'Doodles'


admin_site = MyAdminSite(name='myadmin')
admin_site.index_template = "admin/custom_index.html"
admin_site.register(User)


class DoodleAdmin(admin.ModelAdmin):

    list_display = ("created_at", "admin_thumbnail", "active", "owner")
    readonly_fields = ('admin_thumbnail',)
    list_editable = ["active"]
    # admin_thumbnail = bla

    def epaper_format(self, obj):
        return obj.to_epaper_format()

    def admin_thumbnail(self, obj):
        return mark_safe(
            f"{AdminThumbnail(image_field='processed_image')(obj)}</div>".replace(
                "<img", "<img width=300"
            )
        )


admin_site.register(Doodle, DoodleAdmin)
