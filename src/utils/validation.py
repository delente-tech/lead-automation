import re

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^\d{10}$")
PINCODE_RE = re.compile(r"^\d{6}$")
TEXT_ONLY_RE = re.compile(r"^[A-Za-z\s]+$")

def normalize_phone(raw):
    """Normalize phone number to extract last 10 digits."""
    if not raw:
        return None
    s = ''.join(ch for ch in str(raw) if ch.isdigit())
    return s[-10:] if len(s) >= 10 else None

def normalize_pincode(raw):
    """Normalize pincode to extract 6 digits."""
    if not raw:
        return None
    s = ''.join(ch for ch in str(raw) if ch.isdigit())
    return s if len(s) == 6 else None

def normalize_text_field(raw):
    """Normalize text field by stripping whitespace."""
    if raw is None:
        return ""
    return str(raw).strip()

def is_email_ok(email):
    """Validate email format."""
    if not email:
        return False
    return bool(EMAIL_RE.match(normalize_text_field(email)))

def is_phone_ok(phone):
    """Validate phone number (10 digits)."""
    normalized = normalize_phone(phone)
    if not normalized:
        return False
    return bool(PHONE_RE.match(normalized))

def is_pincode_ok(pincode):
    """Validate pincode (6 digits)."""
    normalized = normalize_pincode(pincode)
    if not normalized:
        return False
    return bool(PINCODE_RE.match(normalized))

def is_fullname_ok(full_name):
    """Validate full name (at least 3 characters, contains letters)."""
    normalized = normalize_text_field(full_name)
    if not normalized:
        return False
    return len(normalized) >= 3 and any(c.isalpha() for c in normalized)

def is_location_ok(location):
    """Validate location/city (letters and spaces only, at least 2 characters)."""
    normalized = normalize_text_field(location)
    if not normalized or len(normalized) < 2:
        return False
    return bool(TEXT_ONLY_RE.match(normalized))

def is_state_ok(state):
    """Validate state (letters and spaces only, at least 2 characters)."""
    normalized = normalize_text_field(state)
    if not normalized or len(normalized) < 2:
        return False
    return bool(TEXT_ONLY_RE.match(normalized))

def validate_field(field_name, value):
    """Validate a field based on its name, skipping campaign_name."""
    validators = {
        "email": is_email_ok,
        "phone_number": is_phone_ok,
        "zip_code": is_pincode_ok,
        "full_name": is_fullname_ok,
        "where_do_you_located_in?": is_location_ok,
        "state": is_state_ok
    }
    validator = validators.get(field_name)
    if not validator:
        return True
    return validator(value)