from django.contrib import admin
from django.utils.html import format_html
from flipbook.models import PdfFlipbook


@admin.register(PdfFlipbook)
class PdfFlipbookAdmin(admin.ModelAdmin):
    list_display = ('flipbook_title', 'modified_date', 'admin_thumbnail')
    list_filter = ('modified_date',)
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
