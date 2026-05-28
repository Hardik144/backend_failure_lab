from pydantic import BaseModel


class WithdrawRequest(BaseModel):
    amount_cents: int


class AccountResponse(BaseModel):
    id: int
    balance_cents: int
