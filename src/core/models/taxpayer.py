from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Taxpayer:
    pan: str = ""
    aadhaar: str = ""
    name: str = ""
    dob: str = ""
    filing_status: str = ""
    is_resident: bool = True
    is_director: bool = False
    has_foreign_assets: bool = False
    has_unlisted_equity: bool = False
    email: str = ""
    mobile: str = ""
