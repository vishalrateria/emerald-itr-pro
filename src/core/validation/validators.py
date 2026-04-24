import re


def validate_pan(pan: str) -> bool:
    return bool(re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", pan.upper())) if pan else False


def validate_aadhaar(aadhaar: str) -> bool:
    return bool(re.match(r"^[0-9]{12}$", aadhaar)) if aadhaar else False


def validate_ifsc(ifsc: str) -> bool:
    return bool(re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", ifsc.upper())) if ifsc else False


def validate_bank_account(acc: str) -> bool:
    if not acc:
        return False
    return bool(re.match(r"^\d{9,18}$", acc)) and not acc.startswith("0")


def validate_mobile(mobile: str) -> bool:
    return bool(re.match(r"^[6789][0-9]{9}$", mobile)) if mobile else False


def validate_email(email: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)) if email else False
