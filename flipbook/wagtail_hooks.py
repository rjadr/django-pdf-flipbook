"""
Wagtail snippet registration for PdfFlipbook.

Registers PdfFlipbook as a Wagtail snippet with a proper list view:
thumbnail column, title, collection, sort order, and modified date.

This module is only active when Wagtail is installed. If Wagtail is not
present, importing this module is safe — nothing is registered.
"""

try:
    from wagtail.snippets.models import register_snippet
    from wagtail.snippets.views.snippets import SnippetViewSet
    from wagtail.admin.ui.tables import Column, TitleColumn, DateColumn
    from wagtail.admin.panels import FieldPanel

    from flipbook.models import FlipbookCategory, PdfFlipbook

    class FlipbookCategoryViewSet(SnippetViewSet):
        """
        Registers FlipbookCategory as a snippet so Wagtail's FK chooser
        widget on PdfFlipbook renders a "+" button for inline category
        creation (modal, no page navigation required).

        Hidden from the sidebar — categories are managed directly from
        the PdfFlipbook edit form via the chooser widget.
        """

        model = FlipbookCategory
        icon = "folder-open-inverse"
        menu_label = "Flipbook Categories"
        menu_order = 201
        add_to_admin_menu = False  # No sidebar entry; managed via PdfFlipbook chooser
        list_display = ["name"]
        search_fields = ("name",)
        panels = [FieldPanel("name")]

    register_snippet(FlipbookCategoryViewSet)

    class ThumbnailColumn(Column):
        """
        Renders a small thumbnail image in the Wagtail snippet list.

        ``get_value`` returns the ImageFieldFile; the template checks
        ``value.name`` before calling ``value.url`` so empty fields are safe.
        """

        cell_template_name = "flipbook/admin/thumbnail_cell.html"

        def get_value(self, instance):
            return instance.flipbook_image

    _list_display = [
        ThumbnailColumn("flipbook_image", label="", width="80px"),
        TitleColumn(
            "flipbook_title",
            label="Title",
            url_name="wagtailsnippets_flipbook_pdfflipbook:edit",
        ),
        Column("category", label="Category", sort_key="category__name"),
        Column("sort_order", label="Order", sort_key="sort_order"),
        DateColumn("modified_date", label="Modified", sort_key="modified_date"),
    ]

    class PdfFlipbookViewSet(SnippetViewSet):
        model = PdfFlipbook
        icon = "doc-full"
        menu_label = "PDF Flipbooks"
        menu_order = 200
        add_to_admin_menu = True
        list_display = _list_display
        list_filter = ("category",)
        search_fields = ("flipbook_title",)
        ordering = ("sort_order", "-modified_date")

        panels = [
            FieldPanel("flipbook_title"),
            FieldPanel("flipbook_document"),
            FieldPanel("sort_order"),
            FieldPanel("category"),
        ]

    register_snippet(PdfFlipbookViewSet)

except ImportError:
    pass
