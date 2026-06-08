import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logger import logger
from src.config.security import verify_hash
from src.domain.enums import TransactionStatus
from src.domain.models import LedgerEntry, Transaction, User
from src.schemas.ledger_schemas import DepositCreate, TransferCreate
from src.selectors.ledger_selectors import (
    get_transaction_by_idempotency_key,
    get_wallet_balance,
)
from src.selectors.wallet_selectors import get_wallet_by_id


async def transfer_funds(
    session: AsyncSession,
    sender: User,
    from_wallet_id: uuid.UUID,
    transfer_data: TransferCreate,
) -> Transaction:
    log = logger.bind(idempotency_key=transfer_data.idempotency_key)

    log.info(
        "transfer_initiated",
        sender_id=str(sender.id),
        amount=float(transfer_data.amount),
    )
    existing_txn = await get_transaction_by_idempotency_key(
        session, key=transfer_data.idempotency_key
    )
    if existing_txn:
        return existing_txn

    if not verify_hash(transfer_data.transaction_pin, sender.transaction_pin_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid transaction PIN."
        )

    first_id, second_id = sorted([from_wallet_id, transfer_data.to_wallet_id])

    first_wallet = await get_wallet_by_id(session, first_id, lock=True)
    second_wallet = await get_wallet_by_id(session, second_id, lock=True)

    sender_wallet = first_wallet if first_wallet.id == from_wallet_id else second_wallet
    receiver_wallet = (
        second_wallet
        if second_wallet.id == transfer_data.to_wallet_id
        else first_wallet
    )

    if sender_wallet and receiver_wallet and sender_wallet.id == receiver_wallet.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transfer funds to the same wallet.",
        )

    if not sender_wallet or sender_wallet.user_id != sender.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sender wallet not found"
        )

    if not receiver_wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Receiver wallet not found"
        )

    if sender_wallet.is_frozen or receiver_wallet.is_frozen:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="One of the wallet is frozen"
        )

    if sender_wallet.currency != receiver_wallet.currency:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Currency mismatch"
        )

    current_balance = await get_wallet_balance(session, wallet_id=sender_wallet.id)
    if current_balance < transfer_data.amount:
        log.warn(
            "transfer_failed",
            reason="insufficient_funds",
            current_balance=float(current_balance),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds"
        )

    try:
        new_transaction = Transaction(
            idempotency_key=transfer_data.idempotency_key,
            status=TransactionStatus.COMPLETED,
            description=transfer_data.description,
        )
        session.add(new_transaction)
        await session.flush()

        sender_entry = LedgerEntry(
            transaction_id=new_transaction.id,
            wallet_id=sender_wallet.id,
            amount=-transfer_data.amount,
        )
        receiver_entry = LedgerEntry(
            transaction_id=new_transaction.id,
            wallet_id=receiver_wallet.id,
            amount=transfer_data.amount,
        )

        session.add_all([sender_entry, receiver_entry])
        await session.commit()
        await session.refresh(new_transaction)
        log.info("transfer_successful", transaction_id=str(new_transaction.id))
        return new_transaction
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction failed due to an internal error.",
        )


async def mock_deposit_funds(
    session: AsyncSession, wallet_id: uuid.UUID, deposit_data: DepositCreate
) -> Transaction:
    existing_txn = await get_transaction_by_idempotency_key(
        session, deposit_data.idempotency_key
    )
    if existing_txn:
        return existing_txn

    wallet = await get_wallet_by_id(session, wallet_id)

    if not wallet or wallet.is_frozen:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet not found or is frozen",
        )

    try:
        new_transaction = Transaction(
            idempotency_key=deposit_data.idempotency_key,
            status=TransactionStatus.COMPLETED,
            description=deposit_data.description,
        )
        session.add(new_transaction)
        await session.flush()

        credit_entry = LedgerEntry(
            transaction_id=new_transaction.id,
            wallet_id=wallet.id,
            amount=deposit_data.amount,
        )
        session.add(credit_entry)
        await session.commit()
        await session.refresh(new_transaction)
        return new_transaction
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Deposit failed",
        )
