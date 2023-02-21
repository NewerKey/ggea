import typing

from src.models.db.account import Account
from src.models.schema.account import AccountInSignin, AccountInSignup, AccountInUpdate, CurrentAccountInRead

Accounts = typing.Sequence[Account] | list[Account] | set[Account]
AccountRetriever = AccountInSignin | CurrentAccountInRead
AccountForInput = AccountInSignup | AccountInUpdate
