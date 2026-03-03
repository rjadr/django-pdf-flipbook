"""
Optional Django CMS plugin for embedding a PDF flipbook grid on any CMS page.

This is different from the apphook in ``cms_apps.py``:

- **Apphook** (``cms_apps.py``): mounts the entire ``/flipbook/`` URL tree
  onto a CMS page — gives editors a standalone library page.
- **CMSPlugin** (this file): lets editors *drop a flipbook grid into any
  existing page layout* via the standard "Add plugin" button, just like a
  text or image plugin.

Requires Django CMS::

    pip install "django-pdf-flipbook[cms]"

Then add to ``INSTALLED_APPS``::

    INSTALLED_APPS = [
        ...
        'flipbook',
        'cms',
        ...
    ]

Run migrations so the plugin model table is created::

    python manage.py makemigrations flipbook
    python manage.py migrate
"""

try:
    from cms.plugin_base import CMSPluginBase
    from cms.plugin_pool import plugin_pool

    from flipbook.models import FlipbookCollectionPluginModel

    @plugin_pool.register_plugin
    class FlipbookCollectionPlugin(CMSPluginBase):
        """Drop a DearFlip PDF grid into any Django CMS placeholder.

        Editors configure:
        - **Heading** — optional title shown above the grid
        - **Collection ID** — Wagtail/internal collection pk to filter;
          leave blank to show all PDFs
        """

        model = FlipbookCollectionPluginModel
        name = "PDF Flipbook Collection"
        render_template = "flipbook/cms_plugins/flipbook_collection.html"
        cache = False

        def render(self, context, instance, placeholder):
            from flipbook.models import PdfFlipbook

            qs = PdfFlipbook.objects.select_related('category').all()
            if instance.category_id:
                qs = qs.filter(category_id=instance.category_id)
            context["documents"] = qs
            context["instance"] = instance
            return context

except ImportError:
    pass
