from __future__ import annotations

import typing

from _algopy_testing.protocols import UInt64Backed
from _algopy_testing.utils import resolve_asset_index

if typing.TYPE_CHECKING:
    import algopy


T = typing.TypeVar("T")


class AssetFields(typing.TypedDict, total=False):
    total: algopy.UInt64
    decimals: algopy.UInt64
    default_frozen: bool
    unit_name: algopy.Bytes
    name: algopy.Bytes
    url: algopy.Bytes
    metadata_hash: algopy.Bytes
    manager: algopy.Account
    reserve: algopy.Account
    freeze: algopy.Account
    clawback: algopy.Account
    creator: algopy.Account


class Asset(UInt64Backed):
    def __init__(self, asset_id: algopy.UInt64 | int = 0):
        from algopy import UInt64

        self.id = asset_id if isinstance(asset_id, UInt64) else UInt64(asset_id)

    @property
    def int_(self) -> int:
        return self.id.value

    @classmethod
    def from_int(cls, value: int, /) -> typing.Self:
        return cls(value)

    def balance(self, account: algopy.Account) -> algopy.UInt64:
        from _algopy_testing.context_helpers import lazy_context

        account_data = lazy_context.get_account_data(account.public_key)

        if not account_data:
            raise ValueError("Account not found in testing context!")

        if int(self.id) not in account_data.opted_asset_balances:
            raise ValueError(
                "The asset is not opted into the account! "
                "Use `ctx.any.account(opted_asset_balances={{ASSET_ID: VALUE}})` "
                "to set emulated opted asset into the account."
            )

        return account_data.opted_asset_balances[self.id]

    def frozen(self, _account: algopy.Account) -> bool:
        # TODO: 1.0 expand data structure on AccountContextData.opted_asset_balances
        #       to support frozen attribute
        raise NotImplementedError(
            "The 'frozen' method is being executed in a python testing context. "
            "Please mock this method using your python testing framework of choice."
        )

    @property
    def fields(self) -> AssetFields:
        from _algopy_testing.context_helpers import lazy_context

        return lazy_context.get_asset_data(resolve_asset_index(self.id))

    def __getattr__(self, name: str) -> typing.Any:
        try:
            return self.fields[name]  # type: ignore[literal-required]
        except KeyError:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            ) from None

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Asset):
            return self.id == other.id
        return self.id == other

    def __bool__(self) -> bool:
        return self.id != 0

    def __hash__(self) -> int:
        return hash(self.id)
