from sqlmodel import Session, select

from mtmai.models.models import (
    Account,
    AccountBase,
)


class AccountCreate(AccountBase):
    pass


def create_account(
    *, session: Session, item_in: AccountCreate, owner_id: str
) -> Account:
    account = Account.model_validate(item_in, update={"owner_id": owner_id})
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def get_account_by_user_id(*, session: Session, owner_id: str) -> Account:
    statement = select(Account).where(Account.owner_id == owner_id)
    account_item = session.exec(statement).first()
    return account_item
