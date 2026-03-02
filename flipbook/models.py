# -*- coding: utf-8 -*-
import logging
from io import BytesIO

import magic
from pdf2image import convert_from_bytes

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import FileField
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.crypto import get_random_string

logger = logging.getLogger(__name__)


def validate_pdf_mime_type(upload):
    """Reject uploads whose magic bytes do not identify them as a PDF."""
    upload.seek(0)
    content_type = magic.from_buffer(upload.read(1024), mime=True)
    upload.seek(0)
    if content_type != 'application/pdf':
        raise ValidationError("Uploaded file is not a valid PDF (detected: %(ct)s).",
                              params={'ct': content_type})


class PdfFlipbook(models.Model):
    flipbook_title = models.CharField(max_length=24, blank=False, null=False)
    modified_date = models.DateTimeField(default=timezone.now, blank=True)
    flipbook_document = models.FileField(
        upload_to="flipbook/",
        blank=False,
        null=False,
        validators=[FileExtensionValidator(['pdf']), validate_pdf_mime_type],
    )
    flipbook_image = models.ImageField(upload_to="flipbook/", editable=False, blank=True)
    sort_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Lower numbers appear first. Items with the same number are sorted by upload date.",
    )
    # Optional Wagtail collection support. Requires wagtail to be installed.
    # FK is defined as a lazy string reference so the model loads fine without Wagtail.
    collection = models.ForeignKey(
        'wagtailcore.Collection',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='flipbook_documents',
        help_text="Wagtail collection this PDF belongs to (optional).",
    )

    def save(self, *args, **kwargs):
        if self.pk:  # updating an existing object
            try:
                old = PdfFlipbook.objects.get(pk=self.pk)
            except PdfFlipbook.DoesNotExist:
                old = None

            if old and self.flipbook_document and old.flipbook_document:
                if self.flipbook_document != old.flipbook_document:
                    old.flipbook_document.delete(save=False)
                    if old.flipbook_image:
                        old.flipbook_image.delete(save=False)
                    self._create_image = True
        else:  # new object
            self._create_image = True

        super().save(*args, **kwargs)

    def __str__(self):
        return "[{}] {} {}".format(self.flipbook_title, self.flipbook_document, self.flipbook_image)

    class Meta:
        ordering = ['sort_order', '-modified_date']


@receiver(post_save, sender=PdfFlipbook, dispatch_uid="create_image_after_save")
def create_image_after_save(sender, instance, **kwargs):
    """Generate a thumbnail after a PdfFlipbook is saved."""
    if not getattr(instance, '_create_image', False):
        return

    img_name = create_thumbnail_from_pdf(instance.flipbook_document.name)
    if img_name:
        # Use .update() so this signal is NOT re-triggered (no recursion risk).
        PdfFlipbook.objects.filter(pk=instance.pk).update(flipbook_image=img_name)


def create_thumbnail_from_pdf(document_name):
    """Generate a 300-px-wide PNG thumbnail from the first page of a PDF.

    Uses pdf2image / poppler — no ImageMagick policy headaches.
    Works with any Django storage backend (local, S3, GCS, …).

    Args:
        document_name: Storage-relative path of the PDF (e.g. 'flipbook/foo.pdf').

    Returns:
        Storage-relative path of the saved thumbnail, or None on failure.
    """
    try:
        with default_storage.open(document_name, 'rb') as f:
            pdf_bytes = f.read()

        pages = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, dpi=150)
        if not pages:
            return None

        img = pages[0]
        width, height = img.size
        if width > 300:
            img = img.resize((300, int(height * 300 / width)))

        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        img_name = 'flipbook/{}.png'.format(get_random_string(12))
        default_storage.save(img_name, ContentFile(buf.read()))
        return img_name

    except Exception:
        logger.exception("Thumbnail generation failed for '%s'.", document_name)
        return None


@receiver(post_delete, sender=PdfFlipbook, dispatch_uid="delete_docs_after_delete")
def file_cleanup(sender, instance, **kwargs):
    """Delete PDF and thumbnail files when a PdfFlipbook instance is deleted."""
    for field in sender._meta.get_fields():
        if not isinstance(field, FileField):
            continue
        file_field = getattr(instance, field.name)
        if not file_field or not file_field.name:
            continue
        # Only delete if no other row still references the same file.
        still_used = sender._default_manager.filter(
            **{field.name: file_field.name}
        ).exists()
        if not still_used:
            try:
                default_storage.delete(file_field.name)
            except Exception:
                logger.exception("Could not delete file '%s'.", file_field.name)
