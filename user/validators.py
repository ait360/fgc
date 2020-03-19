import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class PhoneNumberValidator(validators.RegexValidator):
    regex = r'^(\d{11})$'
    message = _(
        'Enter a valid phone number'
    )
    flags = 0