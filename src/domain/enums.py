from enum import Enum


class Role(str, Enum):
    USER = "USER"
    COMPLIANCE = "COMPLIANCE"
    ADMIN = "ADMIN"
