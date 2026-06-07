from enum import Enum


class Role(str, Enum):
    USER = "USER"
    COMPLIANCE = "COMPLIANCE"
    ADMIN = "ADMIN"


class Currency(str, Enum):
    NPR = "NPR"
    USD = "USD"
    INR = "INR"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
