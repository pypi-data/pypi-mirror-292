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

class AccessMetadataValue(BaseModel):
    """
    An access control value. Provider should only be used if you are a service provide licensing data. In that case  the provider value must match your domain.  # noqa: E501
    """
    value: constr(strict=True, max_length=2048, min_length=0) = Field(...)
    provider: Optional[constr(strict=True, max_length=50, min_length=0)] = None
    __properties = ["value", "provider"]

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
    def from_json(cls, json_str: str) -> AccessMetadataValue:
        """Create an instance of AccessMetadataValue from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # set to None if provider (nullable) is None
        # and __fields_set__ contains the field
        if self.provider is None and "provider" in self.__fields_set__:
            _dict['provider'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> AccessMetadataValue:
        """Create an instance of AccessMetadataValue from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return AccessMetadataValue.parse_obj(obj)

        _obj = AccessMetadataValue.parse_obj({
            "value": obj.get("value"),
            "provider": obj.get("provider")
        })
        return _obj
