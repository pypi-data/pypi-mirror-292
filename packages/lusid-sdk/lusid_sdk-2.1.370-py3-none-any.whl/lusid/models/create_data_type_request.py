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
from pydantic.v1 import BaseModel, Field, StrictStr, conlist, constr, validator
from lusid.models.create_unit_definition import CreateUnitDefinition
from lusid.models.reference_data import ReferenceData

class CreateDataTypeRequest(BaseModel):
    """
    CreateDataTypeRequest
    """
    scope: constr(strict=True, max_length=64, min_length=1) = Field(..., description="The scope that the data type will be created in.")
    code: constr(strict=True, max_length=64, min_length=1) = Field(..., description="The code of the data type. Together with the scope this uniquely defines the data type.")
    type_value_range: StrictStr = Field(..., alias="typeValueRange", description="Indicates the range of data acceptable by a data type. The available values are: Open, Closed")
    display_name: constr(strict=True, max_length=512, min_length=1) = Field(..., alias="displayName", description="The display name of the data type.")
    description: constr(strict=True, max_length=1024, min_length=0) = Field(..., description="The description of the data type.")
    value_type: StrictStr = Field(..., alias="valueType", description="The expected type of the values. The available values are: String, Int, Decimal, DateTime, Boolean, Map, List, PropertyArray, Percentage, Code, Id, Uri, CurrencyAndAmount, TradePrice, Currency, MetricValue, ResourceId, ResultValue, CutLocalTime, DateOrCutLabel, UnindexedText")
    acceptable_values: Optional[conlist(StrictStr)] = Field(None, alias="acceptableValues", description="The acceptable set of values for this data type. Only applies to 'open' value type range.")
    unit_schema: Optional[StrictStr] = Field(None, alias="unitSchema", description="The schema of the data type's units. The available values are: NoUnits, Basic, Iso4217Currency")
    acceptable_units: Optional[conlist(CreateUnitDefinition)] = Field(None, alias="acceptableUnits", description="The definitions of the acceptable units.")
    reference_data: Optional[ReferenceData] = Field(None, alias="referenceData")
    __properties = ["scope", "code", "typeValueRange", "displayName", "description", "valueType", "acceptableValues", "unitSchema", "acceptableUnits", "referenceData"]

    @validator('scope')
    def scope_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^[a-zA-Z0-9\-_]+$", value):
            raise ValueError(r"must validate the regular expression /^[a-zA-Z0-9\-_]+$/")
        return value

    @validator('code')
    def code_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^[a-zA-Z0-9\-_]+$", value):
            raise ValueError(r"must validate the regular expression /^[a-zA-Z0-9\-_]+$/")
        return value

    @validator('type_value_range')
    def type_value_range_validate_enum(cls, value):
        """Validates the enum"""
        if value not in ('Open', 'Closed'):
            raise ValueError("must be one of enum values ('Open', 'Closed')")
        return value

    @validator('display_name')
    def display_name_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^[\s\S]*$", value):
            raise ValueError(r"must validate the regular expression /^[\s\S]*$/")
        return value

    @validator('description')
    def description_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^[\s\S]*$", value):
            raise ValueError(r"must validate the regular expression /^[\s\S]*$/")
        return value

    @validator('value_type')
    def value_type_validate_enum(cls, value):
        """Validates the enum"""
        if value not in ('String', 'Int', 'Decimal', 'DateTime', 'Boolean', 'Map', 'List', 'PropertyArray', 'Percentage', 'Code', 'Id', 'Uri', 'CurrencyAndAmount', 'TradePrice', 'Currency', 'MetricValue', 'ResourceId', 'ResultValue', 'CutLocalTime', 'DateOrCutLabel', 'UnindexedText'):
            raise ValueError("must be one of enum values ('String', 'Int', 'Decimal', 'DateTime', 'Boolean', 'Map', 'List', 'PropertyArray', 'Percentage', 'Code', 'Id', 'Uri', 'CurrencyAndAmount', 'TradePrice', 'Currency', 'MetricValue', 'ResourceId', 'ResultValue', 'CutLocalTime', 'DateOrCutLabel', 'UnindexedText')")
        return value

    @validator('unit_schema')
    def unit_schema_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('NoUnits', 'Basic', 'Iso4217Currency'):
            raise ValueError("must be one of enum values ('NoUnits', 'Basic', 'Iso4217Currency')")
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
    def from_json(cls, json_str: str) -> CreateDataTypeRequest:
        """Create an instance of CreateDataTypeRequest from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of each item in acceptable_units (list)
        _items = []
        if self.acceptable_units:
            for _item in self.acceptable_units:
                if _item:
                    _items.append(_item.to_dict())
            _dict['acceptableUnits'] = _items
        # override the default output from pydantic by calling `to_dict()` of reference_data
        if self.reference_data:
            _dict['referenceData'] = self.reference_data.to_dict()
        # set to None if acceptable_values (nullable) is None
        # and __fields_set__ contains the field
        if self.acceptable_values is None and "acceptable_values" in self.__fields_set__:
            _dict['acceptableValues'] = None

        # set to None if acceptable_units (nullable) is None
        # and __fields_set__ contains the field
        if self.acceptable_units is None and "acceptable_units" in self.__fields_set__:
            _dict['acceptableUnits'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> CreateDataTypeRequest:
        """Create an instance of CreateDataTypeRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return CreateDataTypeRequest.parse_obj(obj)

        _obj = CreateDataTypeRequest.parse_obj({
            "scope": obj.get("scope"),
            "code": obj.get("code"),
            "type_value_range": obj.get("typeValueRange"),
            "display_name": obj.get("displayName"),
            "description": obj.get("description"),
            "value_type": obj.get("valueType"),
            "acceptable_values": obj.get("acceptableValues"),
            "unit_schema": obj.get("unitSchema"),
            "acceptable_units": [CreateUnitDefinition.from_dict(_item) for _item in obj.get("acceptableUnits")] if obj.get("acceptableUnits") is not None else None,
            "reference_data": ReferenceData.from_dict(obj.get("referenceData")) if obj.get("referenceData") is not None else None
        })
        return _obj
