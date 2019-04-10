# django-pdf-flipbook
A Django app that displays a pdf library in a grid and lets you read them as flipbooks.

## Installation
- Copy the `flipbook` folder to the root of your django project.

Install the following requirements:
- Install [Imagemagick](http://docs.wand-py.org/en/0.4.4/guide/install.html#install-imagemagick-on-debian-ubuntu) for thumbnail generation
- `pip install Wand`
- `pip install python-magic`
- `pip install Pillow`

For installation on Max OS X:
- Install Ghostscript: `$ brew install ghostscript`
- When running into an 'ImportError: MagickWand shared library not found.' on Mac OS X, try [this solution](https://stackoverflow.com/questions/37011291/python-wand-image-is-not-recognized/41772062#41772062)


In settings.py add:
- `'flipbook',` to `INSTALLED_APPS`
- 
```
DATA_DIR = os.path.dirname(os.path.dirname(__file__))
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(DATA_DIR, 'media')
TEMP_ROOT = os.path.join(DATA_DIR, 'media/tmp')
```

In urls.py add:
- `from django.urls import include, path`
- `path('flipbook/', include('flipbook.urls')),` to urlpatterns
- When running locally using runserver also add to urls.py:
```
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
```
- 
```
if settings.DEBUG:
    urlpatterns = [
        url(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        ] + staticfiles_urlpatterns() + urlpatterns
```

Then run:
- `$ python manage.py makemigrations flipbook`
- `$ python manage.py migrate flipbook`
- `$ python manage.py runserver`

Add the Flipbook app to a page and upload the pdfs via the admin interface.

## Flipbook plugins
I have implemented [pdfjs-flipbook](https://github.com/iberan/pdfjs-flipbook) by default, which is a bit buggy but free. However, I recommend using [dFlip PDF FlipBook jQuery Plugin](https://codecanyon.net/item/dflip-flipbook-jquery-plugin/15834127). Simply swap the `index.html` files in the templates dir, and populate `flipbook/static/flipbook/dflip/` with the `js`, `sound`, `images`, `fonts` and `css` folders from the [dFlip PDF FlipBook jQuery Plugin](https://codecanyon.net/item/dflip-flipbook-jquery-plugin/15834127).

Change the dependency URLS in dflip.js as follows and you're good to go: 
```
    pdfjsSrc: url + "js/libs/pdf.min.js",
    pdfjsCompatibilitySrc: url + "js/libs/compatibility.js",
    pdfjsWorkerSrc: url + "js/libs/pdf.worker.min.js",
    threejsSrc: url + "js/libs/three.min.js",
    mockupjsSrc: url + "js/libs/mockup.min.js",
    soundFile: url + "sound/turn2.mp3",
    imagesLocation: url + "images",
    imageResourcesPath: url + "images/pdfjs/",
    cMapUrl: url + "cmaps/", 
``` 
## 'not authorized' policy error
If you get a 'not authorized' policy error when uploading a pdf, this has to do with recent changes to ImageMagick. A workaround can be found [here](https://github.com/HazyResearch/fonduer/issues/170). Then restart apache.
