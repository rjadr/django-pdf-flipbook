from django.apps import apps
from django.contrib import admin
from django.utils.html import format_html
from flipbook.models import PdfFlipbook

_wagtail = apps.is_installed('wagtail')


@admin.register(PdfFlipbook)
class PdfFlipbookAdmin(admin.ModelAdmin):
    list_display = (
        'admin_thumbnail',
        'flipbook_title',
        'sort_order',
        *(['collection'] if _wagtail else []),
        'modified_date',
    )
    list_editable = ('sort_order',)
    list_filter = (
        'modified_date',
        *(['collection'] if _wagtail else []),
    )
    search_fields = ('flipbook_title',)
    readonly_fields = ('flipbook_image', 'modified_date')

    def admin_thumbnail(self, obj):
        if obj.flipbook_image:
            return format_html(
                '<img src="{}" width="50" height="70" style="object-fit:cover;border-radius:3px;" />',
                obj.flipbook_image.url,
            )
        return 'No image'

    admin_thumbnail.short_description = 'Thumbnail'
