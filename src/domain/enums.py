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


class Permission(str, Enum):
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    USERS_BAN = "users:ban"

    WALLETS_READ = "wallets:read"
    WALLETS_FREEZE = "wallets:freeze"

    LEDGER_READ = "ledger:read"

    KYC_REVIEW = "kyc:review"
    KYC_READ = "kyc:read"


ROLE_PERMISSIONS = {
    Role.ADMIN: {
        Permission.USERS_READ,
        Permission.USERS_BAN,
        Permission.USERS_WRITE,
        Permission.WALLETS_FREEZE,
        Permission.WALLETS_READ,
        Permission.LEDGER_READ,
        Permission.KYC_REVIEW,
        Permission.KYC_READ,
    },
    Role.COMPLIANCE: {
        Permission.USERS_READ,
        Permission.WALLETS_READ,
        Permission.WALLETS_FREEZE,
        Permission.LEDGER_READ,
        Permission.KYC_REVIEW,
        Permission.KYC_READ,
    },
    Role.USER: set(),
}


class AccountTier(str, Enum):
    TIER_1 = "TIER_1"  # Unverified (Daily limit: 1000)
    TIER_2 = "TIER_2"  # ID verified (Daily limit: 50,000)
    TIER_3 = "TIER_3"  # Address verified (Daily limit: 1,000,000)


class KYCStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
