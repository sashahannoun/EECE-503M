# validators.py
#
# validators for file uploads, etc.

from django.utils.translation import gettext as _

from helpdesk import settings as helpdesk_settings

# TODO: can we use the builtin Django validator instead?
# see:
# https://docs.djangoproject.com/en/4.0/ref/validators/#fileextensionvalidator


def validate_file_extension(value):
    import os

    from django.core.exceptions import ValidationError

    if not helpdesk_settings.HELPDESK_VALIDATE_ATTACHMENT_TYPES:
        return

    # Lab 2, Part C (Layer 2): validate against a strict allowlist, and reject
    # multi-dot filenames outright. os.path.splitext only sees the *last*
    # extension, so "shell.php.png" would otherwise pass as ".png" while a
    # server whose PHP handler matches ".php" anywhere would still execute it.
    name = os.path.basename(value.name)
    if name.count(".") > 1:
        raise ValidationError(
            _("Filenames with multiple extensions are not allowed: ") + name
        )

    ext = os.path.splitext(name)[1]  # [0] returns path+filename

    if ext.lower() not in helpdesk_settings.HELPDESK_VALID_EXTENSIONS and not (
        ext.lower() == "" or ext.lower() == "."
    ):
        raise ValidationError(_("Unsupported file extension: ") + ext.lower())
