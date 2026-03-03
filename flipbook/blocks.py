"""
Optional Wagtail StreamField blocks for embedding flipbook grids in pages.

Requires Wagtail to be installed::

    pip install "django-pdf-flipbook[wagtail]"

Usage in a Wagtail page model::

    from flipbook.blocks import FlipbookCollectionBlock
    from wagtail.fields import StreamField

    class MyPage(Page):
        body = StreamField([
            ('flipbook', FlipbookCollectionBlock()),
            ...
        ], use_json_field=True)

Then in the page template::

    {% load wagtailcore_tags %}
    {% include_block page.body %}

DearFlip CSS and JS are declared on ``FlipbookCollectionBlock.Media``.
Wagtail collects all block Media objects and deduplicates them, so even if
an editor drops three flipbook blocks on one page the scripts load only once.
"""

try:
    from wagtail import blocks

    class FlipbookCollectionBlock(blocks.StructBlock):
        """Embed a DearFlip flipbook grid for a Wagtail collection.

        Drop this into any StreamField to display a PDF grid on any Wagtail
        page — no separate /flipbook/ URL required.

        Set *collection* to the integer pk of the Wagtail Collection you want
        to display, or leave blank to show all PDFs.
        """

        heading = blocks.CharBlock(
            required=False,
            help_text="Optional heading shown above the grid.",
        )
        category = blocks.IntegerBlock(
            required=False,
            help_text="FlipbookCategory ID (pk) to display. Leave blank for all PDFs.",
        )

        class Meta:
            template = "flipbook/blocks/flipbook_collection_block.html"
            icon = "doc-full"
            label = "PDF Flipbook"

        class Media:
            """
            Declare DearFlip CDN assets here so Wagtail deduplicates them.

            When multiple FlipbookCollectionBlocks appear on the same page,
            Wagtail merges all block Media objects and emits each URL only once
            — no more triple-loading of jQuery or dflip.min.js.

            ``flipbook_overrides.css`` is a local static file that suppresses
            DearFlip's default hover animation (cover slide-up + title fade).
            """

            css = {
                "all": [
                    "https://cdn.jsdelivr.net/npm/@dearhive/dearflip-jquery-flipbook/dflip/css/dflip.min.css",
                    "https://cdn.jsdelivr.net/npm/@dearhive/dearflip-jquery-flipbook/dflip/css/themify-icons.min.css",
                    "flipbook/css/flipbook_overrides.css",
                ]
            }
            js = [
                "https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js",
                "https://cdn.jsdelivr.net/npm/@dearhive/dearflip-jquery-flipbook/dflip/js/dflip.min.js",
            ]

        def get_context(self, value, parent_context=None):
            from flipbook.models import PdfFlipbook

            ctx = super().get_context(value, parent_context=parent_context)
            qs = PdfFlipbook.objects.select_related('category').all()
            cat_id = value.get("category")
            if cat_id:
                qs = qs.filter(category_id=cat_id)
            ctx["documents"] = qs
            return ctx

    WAGTAIL_AVAILABLE = True

except ImportError:
    WAGTAIL_AVAILABLE = False

    class FlipbookCollectionBlock:  # noqa: F811
        """Stub — install wagtail to use this block."""

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "FlipbookCollectionBlock requires Wagtail. "
                "Install with: pip install django-pdf-flipbook[wagtail]"
            )

