# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    Contact: info@finbourne.com
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""


from __future__ import annotations
import pprint
import re  # noqa: F401
import json


from typing import Any, Dict, Optional
from pydantic.v1 import BaseModel, Field, constr
from lusid.models.transaction_currency_and_amount import TransactionCurrencyAndAmount
from lusid.models.transaction_price_and_type import TransactionPriceAndType

class TransactionFieldMap(BaseModel):
    """
    TransactionFieldMap
    """
    transaction_id: constr(strict=True, max_length=1024, min_length=0) = Field(..., alias="transactionId")
    type: constr(strict=True, max_length=1024, min_length=0) = Field(...)
    source: constr(strict=True, max_length=1024, min_length=0) = Field(...)
    instrument: constr(strict=True, max_length=1024, min_length=0) = Field(...)
    transaction_date: constr(strict=True, max_length=1024, min_length=0) = Field(..., alias="transactionDate")
    settlement_date: constr(strict=True, max_length=1024, min_length=0) = Field(..., alias="settlementDate")
    units: constr(strict=True, max_length=1024, min_length=0) = Field(...)
    transaction_price: Optional[TransactionPriceAndType] = Field(None, alias="transactionPrice")
    transaction_currency: constr(strict=True, max_length=1024, min_length=0) = Field(..., alias="transactionCurrency")
    exchange_rate: Optional[constr(strict=True, max_length=1024, min_length=0)] = Field(None, alias="exchangeRate")
    total_consideration: TransactionCurrencyAndAmount = Field(..., alias="totalConsideration")
    __properties = ["transactionId", "type", "source", "instrument", "transactionDate", "settlementDate", "units", "transactionPrice", "transactionCurrency", "exchangeRate", "totalConsideration"]

    class Config:
        """Pydantic configuration"""
        allow_population_by_field_name = True
        validate_assignment = True

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.dict(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> TransactionFieldMap:
        """Create an instance of TransactionFieldMap from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of transaction_price
        if self.transaction_price:
            _dict['transactionPrice'] = self.transaction_price.to_dict()
        # override the default output from pydantic by calling `to_dict()` of total_consideration
        if self.total_consideration:
            _dict['totalConsideration'] = self.total_consideration.to_dict()
        # set to None if exchange_rate (nullable) is None
        # and __fields_set__ contains the field
        if self.exchange_rate is None and "exchange_rate" in self.__fields_set__:
            _dict['exchangeRate'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> TransactionFieldMap:
        """Create an instance of TransactionFieldMap from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return TransactionFieldMap.parse_obj(obj)

        _obj = TransactionFieldMap.parse_obj({
            "transaction_id": obj.get("transactionId"),
            "type": obj.get("type"),
            "source": obj.get("source"),
            "instrument": obj.get("instrument"),
            "transaction_date": obj.get("transactionDate"),
            "settlement_date": obj.get("settlementDate"),
            "units": obj.get("units"),
            "transaction_price": TransactionPriceAndType.from_dict(obj.get("transactionPrice")) if obj.get("transactionPrice") is not None else None,
            "transaction_currency": obj.get("transactionCurrency"),
            "exchange_rate": obj.get("exchangeRate"),
            "total_consideration": TransactionCurrencyAndAmount.from_dict(obj.get("totalConsideration")) if obj.get("totalConsideration") is not None else None
        })
        return _obj
