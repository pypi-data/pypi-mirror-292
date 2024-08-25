"""types."""

from datetime import datetime
from enum import Enum
from typing import TypedDict

from pydantic import BaseModel

Content = bytes | str


class Account:
    phone: str
    internet: str

    def __str__(self) -> str:
        return f"DSL# {self.internet} | Phone# {self.phone}"

    def __repr__(self) -> str:
        return self.__str__()


class BillStatus(Enum):
    UNKNOWN = 0
    PAID = 1
    UNPAID = 2


class BillAmount:
    amount: float
    currency: str

    def __init__(self, amount: float = 0, currency: str = "LBP") -> None:
        self.amount = amount
        self.currency = currency

        if currency in ["L.L.", "LL", "L.L"]:
            self.currency = "LBP"

    @staticmethod
    def parse(str_val: str):
        amount, _currency = str_val.split(" ")
        amount = float(amount.replace(",", ""))

        return BillAmount(amount, _currency)

    def __str__(self) -> str:
        return f"{self.amount!s} {self.currency}"

    def __repr__(self) -> str:
        return self.__str__()


class Bill:
    date: datetime
    amount: BillAmount
    status: BillStatus

    def __str__(self) -> str:
        if self.status == BillStatus.PAID:
            status = "paid"
        elif self.status == BillStatus.UNPAID:
            status = "not paid"
        else:
            status = "unknown"

        return f"Bill [{self.date.strftime('%b %Y')}], {self.amount}: {status}"

    def __repr__(self) -> str:
        return self.__str__()


class BillInfo:
    total_outstanding: BillAmount
    bills: list[Bill] = []

    def __str__(self) -> str:
        return f"Total outstanding: {self.total_outstanding}"

    def __repr__(self) -> str:
        return self.__str__()


class ConsumptionInfo:
    speed: str
    quota: int
    upload: float
    download: float
    total_consumption: float
    extra_consumption: float
    last_update: datetime

    def __str__(self) -> str:
        return f"Total Consumption: {self.total_consumption} GB; Last update: {self.last_update}"

    def __repr__(self) -> str:
        return self.__str__()


class ErrorResponseContent(TypedDict):
    code: int | str
    message: str


class ErrorResponse(TypedDict):
    error: ErrorResponseContent


class LoginResponse(TypedDict):
    SessionID: str


class ConfigUser(BaseModel):
    username: str
    password: str


class OgeroConfigFile(BaseModel):
    """config file definition."""

    users: list[ConfigUser] | None = None
