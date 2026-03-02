"""
Optional Wagtail StreamField blocks for embedding flipbook grids in pages.

Requires Wagtail to be installed::

    pip install "django-pdf-flipbook[cms]"

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

The block renders the DearFlip CDN scripts automatically so the parent
template does not need to include them.
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
        collection = blocks.IntegerBlock(
            required=False,
            help_text="Wagtail Collection ID (pk) to display. Leave blank for all PDFs.",
        )

        class Meta:
            template = 'flipbook/blocks/flipbook_collection_block.html'
            icon = 'doc-full'
            label = 'PDF Flipbook Collection'

    WAGTAIL_AVAILABLE = True

except ImportError:
    WAGTAIL_AVAILABLE = False

    class FlipbookCollectionBlock:  # noqa: F811
        """Stub — install wagtail to use this block."""
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "FlipbookCollectionBlock requires Wagtail. "
                "Install with: pip install django-pdf-flipbook[cms]"
            )

