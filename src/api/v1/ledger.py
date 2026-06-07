import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.config.database import get_db_session
from src.domain.models import User
from src.schemas.ledger_schemas import (
    DepositCreate,
    LedgerEntryResponse,
    TransferCreate,
)
from src.selectors.ledger_selectors import get_wallet_transactions
from src.selectors.wallet_selectors import get_wallet_by_id
from src.services.ledger_service import mock_deposit_funds, transfer_funds

router = APIRouter(prefix="/wallets", tags=["Ledger"])


@router.post(
    "/{wallet_id}/transfer",
    status_code=status.HTTP_201_CREATED,
    summary="Transfer funds to another wallet",
)
async def perform_transfer(
    wallet_id: uuid.UUID,
    transfer_data: TransferCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    transaction = await transfer_funds(
        session=session,
        sender=current_user,
        from_wallet_id=wallet_id,
        transfer_data=transfer_data,
    )
    return {
        "transaction_id": transaction.id,
        "status": transaction.status,
        "amount_transferred": transfer_data.amount,
        "message": "Transfer successful",
    }


@router.post(
    "/{wallet_id}/deposit",
    status_code=status.HTTP_201_CREATED,
    summary="Simulate loading funds from an external bank",
)
async def mock_deposit(
    wallet_id: uuid.UUID,
    deposit_data: DepositCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    transaction = await mock_deposit_funds(
        session, wallet_id=wallet_id, deposit_data=deposit_data
    )

    return {
        "transaction_id": transaction.id,
        "amount_deposited": deposit_data.amount,
        "message": "Deposit successful",
    }


@router.get(
    "/{wallet_id}/transactions",
    response_model=list[LedgerEntryResponse],
    status_code=status.HTTP_200_OK,
    summary="View wallet transaction history",
)
async def get_transaction_history(
    wallet_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    wallet = await get_wallet_by_id(session, wallet_id)

    if not wallet or wallet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found or unauthorized access",
        )

    entries = await get_wallet_transactions(session, wallet_id)
    return entries
