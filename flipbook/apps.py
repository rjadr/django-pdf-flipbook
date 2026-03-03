import shutil

from django.apps import AppConfig
from django.core import checks


class FlipbookConfig(AppConfig):
    name = "flipbook"
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = "PDF Flipbook"

    def ready(self):
        # Importing models here ensures @receiver-decorated signals are registered.
        import flipbook.models  # noqa: F401


@checks.register(checks.Tags.compatibility)
def check_poppler_installed(app_configs, **kwargs):
    """Warn when Poppler's pdftoppm binary is not on the system PATH.

    pdf2image needs Poppler at runtime to convert PDF pages to images.
    Without it, thumbnail generation will silently fail on every PDF upload.

    System check tag: flipbook.W001
    """
    if app_configs is not None and not any(
        getattr(ac, "name", None) == "flipbook" for ac in app_configs
    ):
        return []

    if shutil.which("pdftoppm") is None:
        return [
            checks.Warning(
                "Poppler (pdftoppm) was not found on the system PATH.",
                hint=(
                    "Install Poppler to enable PDF thumbnail generation.\n"
                    "  macOS:  brew install poppler\n"
                    "  Debian: sudo apt-get install poppler-utils\n"
                    "  Alpine: apk add poppler-utils"
                ),
                obj="flipbook",
                id="flipbook.W001",
            )
        ]
    return []
