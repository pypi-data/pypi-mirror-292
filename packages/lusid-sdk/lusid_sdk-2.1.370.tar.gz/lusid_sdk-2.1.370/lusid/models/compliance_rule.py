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


from typing import Any, Dict, List, Optional, Union
from pydantic.v1 import BaseModel, Field, StrictBool, StrictFloat, StrictInt, StrictStr, conlist, constr, validator
from lusid.models.resource_id import ResourceId
from lusid.models.version import Version

class ComplianceRule(BaseModel):
    """
    ComplianceRule
    """
    scope: constr(strict=True, min_length=1) = Field(...)
    code: constr(strict=True, min_length=1) = Field(...)
    display_name: constr(strict=True, min_length=1) = Field(..., alias="displayName")
    type: constr(strict=True, min_length=1) = Field(...)
    property_key: Optional[StrictStr] = Field(None, alias="propertyKey")
    value: Optional[constr(strict=True, max_length=512, min_length=1)] = None
    address_key: Optional[StrictStr] = Field(None, alias="addressKey")
    lower_bound: Union[StrictFloat, StrictInt] = Field(..., alias="lowerBound")
    upper_bound: Union[StrictFloat, StrictInt] = Field(..., alias="upperBound")
    schedule: constr(strict=True, min_length=1) = Field(...)
    hard_requirement: StrictBool = Field(..., alias="hardRequirement")
    target_portfolio_ids: conlist(ResourceId) = Field(..., alias="targetPortfolioIds")
    description: Optional[StrictStr] = None
    version: Optional[Version] = None
    __properties = ["scope", "code", "displayName", "type", "propertyKey", "value", "addressKey", "lowerBound", "upperBound", "schedule", "hardRequirement", "targetPortfolioIds", "description", "version"]

    @validator('value')
    def value_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if value is None:
            return value

        if not re.match(r"^[\s\S]*$", value):
            raise ValueError(r"must validate the regular expression /^[\s\S]*$/")
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
    def from_json(cls, json_str: str) -> ComplianceRule:
        """Create an instance of ComplianceRule from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of each item in target_portfolio_ids (list)
        _items = []
        if self.target_portfolio_ids:
            for _item in self.target_portfolio_ids:
                if _item:
                    _items.append(_item.to_dict())
            _dict['targetPortfolioIds'] = _items
        # override the default output from pydantic by calling `to_dict()` of version
        if self.version:
            _dict['version'] = self.version.to_dict()
        # set to None if property_key (nullable) is None
        # and __fields_set__ contains the field
        if self.property_key is None and "property_key" in self.__fields_set__:
            _dict['propertyKey'] = None

        # set to None if value (nullable) is None
        # and __fields_set__ contains the field
        if self.value is None and "value" in self.__fields_set__:
            _dict['value'] = None

        # set to None if address_key (nullable) is None
        # and __fields_set__ contains the field
        if self.address_key is None and "address_key" in self.__fields_set__:
            _dict['addressKey'] = None

        # set to None if description (nullable) is None
        # and __fields_set__ contains the field
        if self.description is None and "description" in self.__fields_set__:
            _dict['description'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> ComplianceRule:
        """Create an instance of ComplianceRule from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return ComplianceRule.parse_obj(obj)

        _obj = ComplianceRule.parse_obj({
            "scope": obj.get("scope"),
            "code": obj.get("code"),
            "display_name": obj.get("displayName"),
            "type": obj.get("type"),
            "property_key": obj.get("propertyKey"),
            "value": obj.get("value"),
            "address_key": obj.get("addressKey"),
            "lower_bound": obj.get("lowerBound"),
            "upper_bound": obj.get("upperBound"),
            "schedule": obj.get("schedule"),
            "hard_requirement": obj.get("hardRequirement"),
            "target_portfolio_ids": [ResourceId.from_dict(_item) for _item in obj.get("targetPortfolioIds")] if obj.get("targetPortfolioIds") is not None else None,
            "description": obj.get("description"),
            "version": Version.from_dict(obj.get("version")) if obj.get("version") is not None else None
        })
        return _obj
