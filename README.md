# django-pdf-flipbook

A reusable Django app that displays a PDF library in a responsive grid and lets visitors read them as interactive flipbooks.

> ⚠️ **License notice — DearFlip**
>
> This app uses [DearFlip](https://github.com/dearhive/dearflip-js-flipbook) as its PDF viewer engine,
> loaded from the jsDelivr CDN at runtime.
>
> **DearFlip is licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/) —
> free for personal / non-commercial use only.**
>
> If you are deploying this app on a **commercial website or for a paying client**, you must
> purchase a DearFlip commercial licence from [dearhive.com](https://dearhive.com) before going live.
> The MIT licence of *this* package covers only the Python/Django wrapper code, not the DearFlip engine.

## Requirements

- Python ≥ 3.10
- Django ≥ 4.2
- [Poppler](https://poppler.freedesktop.org/) (used by `pdf2image` for thumbnail generation)

## Installation

### 1. Install system dependency (Poppler)

**macOS**
```bash
brew install poppler
```

**Debian / Ubuntu**
```bash
sudo apt-get install poppler-utils
```

### 2. Install the package

```bash
# Core install (plain Django or Wagtail)
pip install git+https://github.com/rjadr/django-pdf-flipbook.git

# With Wagtail StreamField block + snippet admin
pip install "git+https://github.com/rjadr/django-pdf-flipbook.git#egg=django-pdf-flipbook[wagtail]"

# With Django CMS apphook + CMSPlugin
pip install "git+https://github.com/rjadr/django-pdf-flipbook.git#egg=django-pdf-flipbook[cms]"
```

Python dependencies installed automatically: `Django>=4.2`, `Pillow>=10.0`, `pdf2image>=1.17`, `python-magic>=0.4.27`.

### 3. Configure `settings.py`

```python
INSTALLED_APPS = [
    ...
    'flipbook',
]

DATA_DIR = os.path.dirname(os.path.dirname(__file__))
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(DATA_DIR, 'media')
```

> `TEMP_ROOT` is **no longer required** — thumbnail generation runs entirely through Django's storage API.

### 4. Configure `urls.py`

```python
from django.urls import include, path

urlpatterns = [
    ...
    path('flipbook/', include('flipbook.urls')),
]
```

For local development with `runserver`, also add media file serving:

```python
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 5. Run migrations

```bash
python manage.py makemigrations flipbook
python manage.py migrate flipbook
python manage.py runserver
```

Browse to `http://127.0.0.1:8000/flipbook/` and upload PDFs via the Django admin.

## Template customisation

The app ships with `flipbook/templates/flipbook/base.html` as its base layout. To match your site's look and feel, create `templates/flipbook/base.html` in your **project** and extend your own base:

```html
{% extends "mysite/base.html" %}
```

Django's template loader will prefer your project-level override.

## Flipbook viewer

The app uses [DearFlip](https://github.com/dearhive/dearflip-js-flipbook) (v1.7.36+) loaded from
jsDelivr CDN. No local assets need to be bundled. DearFlip handles its own built-in PDF viewer and
page-turn lightbox.

> **License reminder**: DearFlip is **CC BY-NC-ND 4.0** — non-commercial use only.
> Purchase a licence at [dearhive.com](https://dearhive.com) for commercial deployments.

## Embedding in Wagtail pages (StreamField block)

The recommended way to display flipbooks in Wagtail is via `FlipbookCollectionBlock`. This is a **one-time setup by a developer** per page model — after that, editors can add, remove, and reorder flipbook grids entirely through the Wagtail admin without touching any code.

### 1. Add the block to your page model

```python
# yourapp/models.py
from flipbook.blocks import FlipbookCollectionBlock
from wagtail.fields import StreamField
from wagtail.blocks import RichTextBlock
from wagtail.models import Page

class MyPage(Page):
    body = StreamField([
        ('text', RichTextBlock()),
        ('flipbook', FlipbookCollectionBlock()),  # ← add this
        # ... other blocks
    ], use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]
```

### 2. Add the block to your page template

```html
{# yourapp/templates/yourapp/my_page.html #}
{% load wagtailcore_tags %}
{% include_block page.body %}
```

### 3. Migrate

```bash
python manage.py makemigrations
python manage.py migrate
```

That's it. In the Wagtail admin, editors now see a **"PDF Flipbook Collection"** block option in the page body. Each block has:
- **Heading** — optional title shown above the grid
- **Collection ID** — the pk of the Wagtail Collection to display; leave blank to show all PDFs

The block injects DearFlip CDN scripts automatically — no extra setup in your base template.

## Default library page (plain Django)

For non-Wagtail Django projects, the app provides a ready-made library view at `/flipbook/` that lists all PDFs in a paginated grid with an optional collection filter. This URL is optional for Wagtail users who use the StreamField block instead.

## Collections (Wagtail)

When Wagtail is installed (`pip install "django-pdf-flipbook[wagtail]"`), each flipbook can be assigned to a Wagtail Collection. The library view will show a filter bar at the top letting visitors browse by collection.

```python
# In your flipbook admin, the Collection field appears automatically
# when 'wagtail' is in INSTALLED_APPS.
```

After adding the collection field, re-run migrations:

```bash
python manage.py makemigrations flipbook
python manage.py migrate
```

## Sort order

Each flipbook has a `sort_order` integer field (default `0`). Lower numbers appear first. You can edit it inline in the Django admin list view — click a number, type a new one, and save. Items with equal `sort_order` are sorted newest-first by upload date.

## Key changes in v2.0

| Area | Change |
|---|---|
| Sort order | `sort_order` field; inline-editable in admin; ordering is `sort_order` then newest-first |
| Collections | FK to `wagtailcore.Collection`; collection filter bar in library view (Wagtail only) |
| PDF viewer | Replaced pdfjs-flipbook + fancybox + viewer.html with **DearFlip CDN** (v1.7.36+, ships with PDF.js 4.10) |
| Thumbnail generation | Replaced `Wand` / ImageMagick with `pdf2image` / Poppler — no more "not authorized" policy errors |
| Signal safety | `post_save` uses `.update()` instead of `instance.save()` — no recursion risk |
| Storage | All file I/O via Django's `default_storage` — S3, GCS, Azure Blob work out of the box |
| Validation | MIME magic-byte check added — renaming `.exe` to `.pdf` doesn't bypass validation |
| Pagination | Library view paginated (12 items per page) |
| Admin | Thumbnail preview, search and filter in Django admin |
| URLs | Deprecated `url()` replaced with `path()` (Django 4+) |
| Templates | Namespaced to `flipbook/` and extensible via `flipbook/base.html` |
| CMS | `ugettext_lazy` → `gettext_lazy` (Django 4+) |
| Packaging | Installable via `pip` using `pyproject.toml` |

## django-CMS integration

The app provides two integration points for django-CMS:

### Apphook (`cms_apps.py`)

Mount the entire `/flipbook/` URL tree onto a CMS page. Editors get a
standalone, paginated PDF library page inside their CMS layout.

### CMSPlugin (`cms_plugins.py`)

Drop a flipbook grid *into any existing page layout* via the standard
 **"Add plugin"** button in the CMS toolbar — just like a text or image plugin.

Requires `pip install "django-pdf-flipbook[cms]"` and a migration:

```bash
python manage.py makemigrations flipbook
python manage.py migrate
```

Each plugin instance lets editors set:
- **Heading** — optional title shown above the grid
- **Collection ID** — pk of the collection to display; blank = show all PDFs

## Development

```bash
pip install ".[dev]"
pytest
```

## License

MIT
