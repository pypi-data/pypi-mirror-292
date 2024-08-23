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


from typing import Any, Dict, List, Optional
from pydantic.v1 import BaseModel, Field, StrictStr, conlist, validator
from lusid.models.instrument_event_configuration import InstrumentEventConfiguration
from lusid.models.link import Link
from lusid.models.resource_id import ResourceId
from lusid.models.staged_modifications_info import StagedModificationsInfo
from lusid.models.version import Version

class PortfolioDetails(BaseModel):
    """
    PortfolioDetails
    """
    href: Optional[StrictStr] = Field(None, description="The specific Uniform Resource Identifier (URI) for this resource at the requested effective and asAt datetime.")
    origin_portfolio_id: ResourceId = Field(..., alias="originPortfolioId")
    version: Version = Field(...)
    base_currency: StrictStr = Field(..., alias="baseCurrency", description="The base currency of the transaction portfolio.")
    corporate_action_source_id: Optional[ResourceId] = Field(None, alias="corporateActionSourceId")
    sub_holding_keys: Optional[conlist(StrictStr)] = Field(None, alias="subHoldingKeys")
    instrument_scopes: Optional[conlist(StrictStr)] = Field(None, alias="instrumentScopes", description="The resolution strategy used to resolve instruments of transactions/holdings upserted to the transaction portfolio.")
    accounting_method: Optional[StrictStr] = Field(None, alias="accountingMethod", description=". The available values are: Default, AverageCost, FirstInFirstOut, LastInFirstOut, HighestCostFirst, LowestCostFirst, ProRateByUnits, ProRateByCost, ProRateByCostPortfolioCurrency")
    amortisation_method: Optional[StrictStr] = Field(None, alias="amortisationMethod", description="The amortisation method used by the portfolio for the calculation. The available values are: NoAmortisation, StraightLine, EffectiveYield, StraightLineSettlementDate, EffectiveYieldSettlementDate")
    transaction_type_scope: Optional[StrictStr] = Field(None, alias="transactionTypeScope", description="The scope of the transaction types.")
    cash_gain_loss_calculation_date: Optional[StrictStr] = Field(None, alias="cashGainLossCalculationDate", description="The option when the Cash Gain Loss to be calulated, TransactionDate/SettlementDate. Defaults to SettlementDate.")
    instrument_event_configuration: Optional[InstrumentEventConfiguration] = Field(None, alias="instrumentEventConfiguration")
    amortisation_rule_set_id: Optional[ResourceId] = Field(None, alias="amortisationRuleSetId")
    staged_modifications: Optional[StagedModificationsInfo] = Field(None, alias="stagedModifications")
    links: Optional[conlist(Link)] = None
    __properties = ["href", "originPortfolioId", "version", "baseCurrency", "corporateActionSourceId", "subHoldingKeys", "instrumentScopes", "accountingMethod", "amortisationMethod", "transactionTypeScope", "cashGainLossCalculationDate", "instrumentEventConfiguration", "amortisationRuleSetId", "stagedModifications", "links"]

    @validator('accounting_method')
    def accounting_method_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('Default', 'AverageCost', 'FirstInFirstOut', 'LastInFirstOut', 'HighestCostFirst', 'LowestCostFirst', 'ProRateByUnits', 'ProRateByCost', 'ProRateByCostPortfolioCurrency'):
            raise ValueError("must be one of enum values ('Default', 'AverageCost', 'FirstInFirstOut', 'LastInFirstOut', 'HighestCostFirst', 'LowestCostFirst', 'ProRateByUnits', 'ProRateByCost', 'ProRateByCostPortfolioCurrency')")
        return value

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
    def from_json(cls, json_str: str) -> PortfolioDetails:
        """Create an instance of PortfolioDetails from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of origin_portfolio_id
        if self.origin_portfolio_id:
            _dict['originPortfolioId'] = self.origin_portfolio_id.to_dict()
        # override the default output from pydantic by calling `to_dict()` of version
        if self.version:
            _dict['version'] = self.version.to_dict()
        # override the default output from pydantic by calling `to_dict()` of corporate_action_source_id
        if self.corporate_action_source_id:
            _dict['corporateActionSourceId'] = self.corporate_action_source_id.to_dict()
        # override the default output from pydantic by calling `to_dict()` of instrument_event_configuration
        if self.instrument_event_configuration:
            _dict['instrumentEventConfiguration'] = self.instrument_event_configuration.to_dict()
        # override the default output from pydantic by calling `to_dict()` of amortisation_rule_set_id
        if self.amortisation_rule_set_id:
            _dict['amortisationRuleSetId'] = self.amortisation_rule_set_id.to_dict()
        # override the default output from pydantic by calling `to_dict()` of staged_modifications
        if self.staged_modifications:
            _dict['stagedModifications'] = self.staged_modifications.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in links (list)
        _items = []
        if self.links:
            for _item in self.links:
                if _item:
                    _items.append(_item.to_dict())
            _dict['links'] = _items
        # set to None if href (nullable) is None
        # and __fields_set__ contains the field
        if self.href is None and "href" in self.__fields_set__:
            _dict['href'] = None

        # set to None if sub_holding_keys (nullable) is None
        # and __fields_set__ contains the field
        if self.sub_holding_keys is None and "sub_holding_keys" in self.__fields_set__:
            _dict['subHoldingKeys'] = None

        # set to None if instrument_scopes (nullable) is None
        # and __fields_set__ contains the field
        if self.instrument_scopes is None and "instrument_scopes" in self.__fields_set__:
            _dict['instrumentScopes'] = None

        # set to None if amortisation_method (nullable) is None
        # and __fields_set__ contains the field
        if self.amortisation_method is None and "amortisation_method" in self.__fields_set__:
            _dict['amortisationMethod'] = None

        # set to None if transaction_type_scope (nullable) is None
        # and __fields_set__ contains the field
        if self.transaction_type_scope is None and "transaction_type_scope" in self.__fields_set__:
            _dict['transactionTypeScope'] = None

        # set to None if cash_gain_loss_calculation_date (nullable) is None
        # and __fields_set__ contains the field
        if self.cash_gain_loss_calculation_date is None and "cash_gain_loss_calculation_date" in self.__fields_set__:
            _dict['cashGainLossCalculationDate'] = None

        # set to None if links (nullable) is None
        # and __fields_set__ contains the field
        if self.links is None and "links" in self.__fields_set__:
            _dict['links'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> PortfolioDetails:
        """Create an instance of PortfolioDetails from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return PortfolioDetails.parse_obj(obj)

        _obj = PortfolioDetails.parse_obj({
            "href": obj.get("href"),
            "origin_portfolio_id": ResourceId.from_dict(obj.get("originPortfolioId")) if obj.get("originPortfolioId") is not None else None,
            "version": Version.from_dict(obj.get("version")) if obj.get("version") is not None else None,
            "base_currency": obj.get("baseCurrency"),
            "corporate_action_source_id": ResourceId.from_dict(obj.get("corporateActionSourceId")) if obj.get("corporateActionSourceId") is not None else None,
            "sub_holding_keys": obj.get("subHoldingKeys"),
            "instrument_scopes": obj.get("instrumentScopes"),
            "accounting_method": obj.get("accountingMethod"),
            "amortisation_method": obj.get("amortisationMethod"),
            "transaction_type_scope": obj.get("transactionTypeScope"),
            "cash_gain_loss_calculation_date": obj.get("cashGainLossCalculationDate"),
            "instrument_event_configuration": InstrumentEventConfiguration.from_dict(obj.get("instrumentEventConfiguration")) if obj.get("instrumentEventConfiguration") is not None else None,
            "amortisation_rule_set_id": ResourceId.from_dict(obj.get("amortisationRuleSetId")) if obj.get("amortisationRuleSetId") is not None else None,
            "staged_modifications": StagedModificationsInfo.from_dict(obj.get("stagedModifications")) if obj.get("stagedModifications") is not None else None,
            "links": [Link.from_dict(_item) for _item in obj.get("links")] if obj.get("links") is not None else None
        })
        return _obj
