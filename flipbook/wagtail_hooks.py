"""
Wagtail snippet registration for PdfFlipbook.

Registers PdfFlipbook as a Wagtail snippet with a proper list view:
thumbnail column, title, collection, sort order, and modified date.

This module is only active when Wagtail is installed. If Wagtail is not
present, importing this module is safe — nothing is registered.
"""

try:
    from django.apps import apps
    from wagtail.snippets.models import register_snippet
    from wagtail.snippets.views.snippets import SnippetViewSet
    from wagtail.admin.ui.tables import Column, TitleColumn, DateColumn
    from wagtail.admin.panels import FieldPanel

    from flipbook.models import PdfFlipbook

    class ThumbnailColumn(Column):
        """
        Renders a small thumbnail image in the Wagtail snippet list.

        ``get_value`` returns the ImageFieldFile; the template checks
        ``value.name`` before calling ``value.url`` so empty fields are safe.
        """

        cell_template_name = "flipbook/admin/thumbnail_cell.html"

        def get_value(self, instance):
            return instance.flipbook_image

    # Build list_display dynamically so the collection column only appears
    # when wagtailcore is installed (collection FK may be NULL otherwise).
    _list_display = [
        ThumbnailColumn("flipbook_image", label="", width="80px"),
        TitleColumn(
            "flipbook_title",
            label="Title",
            url_name="wagtailsnippets_flipbook_pdfflipbook:edit",
        ),
        Column("sort_order", label="Order", sort_key="sort_order"),
        DateColumn("modified_date", label="Modified", sort_key="modified_date"),
    ]

    if apps.is_installed("wagtail"):
        _list_display.insert(
            3,
            Column("collection", label="Collection", sort_key="collection__name"),
        )

    class PdfFlipbookViewSet(SnippetViewSet):
        model = PdfFlipbook
        icon = "doc-full"
        menu_label = "PDF Flipbooks"
        menu_order = 200
        add_to_admin_menu = True
        list_display = _list_display
        list_filter = ("collection",) if apps.is_installed("wagtail") else ()
        search_fields = ("flipbook_title",)
        ordering = ("sort_order", "-modified_date")

        panels = [
            FieldPanel("flipbook_title"),
            FieldPanel("flipbook_document"),
            FieldPanel("sort_order"),
            FieldPanel("collection"),
        ]

    register_snippet(PdfFlipbookViewSet)

except ImportError:
    pass
