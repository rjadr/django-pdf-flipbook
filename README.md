# django-pdf-flipbook

A reusable Django app that displays a PDF library in a responsive grid and lets visitors read them as interactive flipbooks.

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
pip install git+https://github.com/rjadr/django-pdf-flipbook.git
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

The app uses [DearFlip](https://github.com/dearhive/dearflip-js-flipbook) (v1.7.36+, CC BY-NC-ND 4.0 — free for personal/non-commercial use) loaded from jsDelivr CDN. No local assets need to be bundled. DearFlip handles its own built-in PDF viewer and page-turn lightbox — no separate `viewer.html` is required.

## Key changes in v2.0

| Area | Change |
|---|---|
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

The app includes an apphook (`flipbook/cms_apps.py`). Attach it to a CMS page to embed the flipbook library inside your CMS layout.

## Development

```bash
pip install ".[dev]"
pytest
```

## License

MIT
