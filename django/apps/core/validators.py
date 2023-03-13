from django.core.validators import RegexValidator,FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

__all__ = ['phone_validator']

phone_validator = RegexValidator(
    regex=r'^\+?3?8?(0\d{9})$',
    message=_("Phone number must be entered in the format '+123456789'. Up to 15 digits allowed.")
)

