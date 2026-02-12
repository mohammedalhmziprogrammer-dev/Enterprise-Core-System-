import re
from rest_framework.exceptions import ValidationError
from django.core.validators import EmailValidator
from . import messages

# Regex Patterns
PHONE_RE = re.compile(r"^\+?\d{7,15}$")
ALPHANUMERIC_RE = re.compile(r'^[a-zA-Z0-9]*$')

def required(value, msg=messages.REQUIRED):
    """
    Check if value is present.
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        raise ValidationError(msg)

def min_len(value, n, msg=None):
    """
    Check minimum length of value.
    """
    if value and len(str(value)) < n:
        error_msg = msg if msg else str(messages.MIN_LENGTH) % {"n": n}
        raise ValidationError(error_msg)

def max_len(value, n, msg=None):
    """
    Check maximum length of value.
    """
    if value and len(str(value)) > n:
        error_msg = msg if msg else str(messages.MAX_LENGTH) % {"n": n}
        raise ValidationError(error_msg)

def phone(value, msg=messages.INVALID_PHONE):
    """
    Validate phone number format.
    """
    if not value:
        return
    if not PHONE_RE.match(str(value)):
        raise ValidationError(msg)

def email(value, msg=messages.INVALID_EMAIL):
    """
    Validate email format.
    """
    if not value:
        return
    validator = EmailValidator(message=msg)
    try:
        validator(value)
    except ValidationError:
        raise ValidationError(msg)

def numeric(value, msg=messages.NUMERIC_ONLY):
    """
    Check if value contains only digits.
    """
    if not value:
        return
    if not str(value).isdigit():
        raise ValidationError(msg)

def alphanumeric(value, msg=messages.ALPHANUMERIC_ONLY):
    """
    Check if value is alphanumeric.
    """
    if not value:
        return
    if not ALPHANUMERIC_RE.match(str(value)):
        raise ValidationError(msg)

def no_start_with_number(value, msg=messages.NO_START_WITH_NUMBER):
    """
    Check that value does not start with a number.
    Useful for name fields.
    """
    if not value:
        return
    if str(value)[0].isdigit():
        raise ValidationError(msg)

def letters_only(value, msg=messages.LETTERS_ONLY):
    """
    Check if value contains only letters (Arabic or English).
    Allows spaces between words.
    """
    if not value:
        return
    # Remove spaces and check if remaining chars are letters
    cleaned = str(value).replace(" ", "")
    if not all(c.isalpha() for c in cleaned):
        raise ValidationError(msg)

def no_spaces(value, msg=messages.NO_SPACES):
    """
    Check that value contains no spaces.
    """
    if not value:
        return
    if " " in str(value):
        raise ValidationError(msg)

def arabic_only(value, msg=messages.ARABIC_ONLY):
    """
    Check if value contains only Arabic letters.
    Allows spaces between words.
    """
    if not value:
        return
    # Arabic Unicode range: \u0600-\u06FF
    arabic_re = re.compile(r'^[\u0600-\u06FF\s]+$')
    if not arabic_re.match(str(value)):
        raise ValidationError(msg)
