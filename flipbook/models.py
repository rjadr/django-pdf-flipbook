# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import FileField
from django.db.models.signals import post_delete, post_save
from django.core.validators import FileExtensionValidator
from django.core.files.storage import default_storage
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.dispatch import receiver
from django.conf import settings
import os
import magic
from wand.image import Image  
from wand.color import Color  

class PdfFlipbook(models.Model):  
    flipbook_title = models.CharField(max_length=24,
                                        blank=False,
                                        null=False)
    modified_date = models.DateTimeField(default=timezone.now,
                                         blank=True)
    flipbook_document = models.FileField(upload_to="flipbook/",
                                            blank=False,
                                            null=False,
                                            validators=[FileExtensionValidator(['pdf'])])
    flipbook_image = models.ImageField(upload_to="flipbook/",  # param optional due to post create
                                          editable=False)


    def save(self, *args, **kwargs):
        if self.pk:  # if the object already exists in the db
            old = PdfFlipbook.objects.get(pk=self.pk)
            old_doc = old.flipbook_document
            old_image = old.flipbook_image

            if self.flipbook_document and old_doc:
                if not self.flipbook_document == old_doc:
                    old_doc.delete(save=False)
                    if old_image:  # delete associated image
                        old_image.delete(save=False)

                    self._create_image = True  # pass to signal
        else:  # if the object is new
            self._create_image = True  # pass to signal

        return super(PdfFlipbook, self).save(*args, **kwargs)

    def __str__(self):
        return "[{}] {} {}".format(self.flipbook_title, self.flipbook_document, self.flipbook_image)

    class Meta:
        ordering = ['-modified_date'] #sort by upload date - newest first

@receiver(post_save, sender=PdfFlipbook, dispatch_uid="create_image_after_save")
def create_image_after_save(sender, instance, **kwargs):  
    """Create image after `PdfFlipbook` object is saved."""
    create_image = getattr(instance, '_create_image', False)

    if create_image:
        pdfpath = os.path.join(settings.MEDIA_ROOT, instance.flipbook_document.name)
        imgpath = create_image_from_pdf(pdfpath)
        instance.flipbook_image = 'flipbook/{}'.format(os.path.basename(imgpath))
        instance._create_image = False  # set to False so infinite loop doesn't occur
        instance.save()

def create_image_from_pdf(pdfpath):  
    """Generate image from pdf.

    Saves the image to the MEDIA_ROOT/images directory

    Args
    ----
        pdfpath (str)
            path to pdf

    Returns
    -------
        path to the saved image
    """
    randname = get_random_string()
    imgtemp = os.path.join(settings.TEMP_ROOT, '{}.png'.format(randname))
    imgsaved = os.path.join(settings.MEDIA_ROOT, 'flipbook', '{}.png'.format(randname))

    # generate temporary image first
    with Image(filename='{}[0]'.format(pdfpath), resolution=300) as img:
        img.background_color = Color('white')
        img.alpha_channel = 'remove'
        if not os.path.exists(settings.TEMP_ROOT):
            os.makedirs(settings.TEMP_ROOT)
        img.save(filename=imgtemp)

    # resize temporary image
    with Image(filename=imgtemp) as img:
        width, height = img.size
        if width > 300:
            ratio = width * 1.0 / 300
            new_width = 300
            new_height = height / ratio
        else:
            new_width = width
            new_height = height
        img.resize(int(new_width), int(new_height))
        img.save(filename=imgsaved)
    # delete temp image file
    os.remove(imgtemp)

    return imgsaved

@receiver(post_delete, sender=PdfFlipbook, dispatch_uid="delete_docs_after_save")
def file_cleanup(sender, **kwargs):
    """
    File cleanup callback used to emulate the old delete
    behavior using signals. Initially django deleted linked
    files when an object containing a File/ImageField was deleted.
    Usage:
    >>> from django.db.models.signals import post_delete
    >>> post_delete.connect(file_cleanup, sender=MyModel, dispatch_uid="mymodel.file_cleanup")
    """
    for fieldname in sender._meta.get_fields():
        try:
            field = sender._meta.get_field(fieldname)
        except:
            field = None
        if field and isinstance(field, FileField):
            inst = kwargs['instance']
            f = getattr(inst, fieldname)
            m = inst.__class__._default_manager
            if hasattr(f, 'path') and os.path.exists(f.path) \
                and not m.filter(**{'%s__exact' % fieldname: getattr(inst, fieldname)})\
                .exclude(pk=inst._get_pk_val()):
                    try:
                        #os.remove(f.path)
                        default_storage.delete(f.path)
                    except:
                        pass
