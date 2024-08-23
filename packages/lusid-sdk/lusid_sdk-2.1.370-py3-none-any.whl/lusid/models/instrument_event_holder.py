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
from pydantic.v1 import BaseModel, Field, StrictInt, StrictStr, conlist, constr, validator
from lusid.models.event_date_range import EventDateRange
from lusid.models.instrument_event import InstrumentEvent
from lusid.models.perpetual_property import PerpetualProperty
from lusid.models.resource_id import ResourceId

class InstrumentEventHolder(BaseModel):
    """
    An instrument event equipped with additional metadata.  # noqa: E501
    """
    instrument_event_id: constr(strict=True, max_length=64, min_length=1) = Field(..., alias="instrumentEventId", description="The unique identifier of this corporate action.")
    corporate_action_source_id: Optional[ResourceId] = Field(None, alias="corporateActionSourceId")
    instrument_identifiers: Dict[str, StrictStr] = Field(..., alias="instrumentIdentifiers", description="The set of identifiers which determine the instrument this event relates to.")
    lusid_instrument_id: constr(strict=True, min_length=1) = Field(..., alias="lusidInstrumentId", description="The LUID for the instrument.")
    instrument_scope: constr(strict=True, min_length=1) = Field(..., alias="instrumentScope", description="The scope of the instrument.")
    description: constr(strict=True, max_length=1024, min_length=0) = Field(..., description="The description of the instrument event.")
    event_date_range: EventDateRange = Field(..., alias="eventDateRange")
    instrument_event: InstrumentEvent = Field(..., alias="instrumentEvent")
    properties: Optional[conlist(PerpetualProperty)] = Field(None, description="The properties attached to this instrument event.")
    sequence_number: Optional[StrictInt] = Field(None, alias="sequenceNumber", description="The order of the instrument event relative others on the same date (0 being processed first). Must be non negative.")
    participation_type: Optional[StrictStr] = Field('Mandatory', alias="participationType", description="Is participation in this event Mandatory, MandatoryWithChoices, or Voluntary.")
    __properties = ["instrumentEventId", "corporateActionSourceId", "instrumentIdentifiers", "lusidInstrumentId", "instrumentScope", "description", "eventDateRange", "instrumentEvent", "properties", "sequenceNumber", "participationType"]

    @validator('instrument_event_id')
    def instrument_event_id_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^[a-zA-Z0-9\-_]+$", value):
            raise ValueError(r"must validate the regular expression /^[a-zA-Z0-9\-_]+$/")
        return value

    @validator('description')
    def description_validate_regular_expression(cls, value):
        """Validates the regular expression"""
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
    def from_json(cls, json_str: str) -> InstrumentEventHolder:
        """Create an instance of InstrumentEventHolder from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of corporate_action_source_id
        if self.corporate_action_source_id:
            _dict['corporateActionSourceId'] = self.corporate_action_source_id.to_dict()
        # override the default output from pydantic by calling `to_dict()` of event_date_range
        if self.event_date_range:
            _dict['eventDateRange'] = self.event_date_range.to_dict()
        # override the default output from pydantic by calling `to_dict()` of instrument_event
        if self.instrument_event:
            _dict['instrumentEvent'] = self.instrument_event.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in properties (list)
        _items = []
        if self.properties:
            for _item in self.properties:
                if _item:
                    _items.append(_item.to_dict())
            _dict['properties'] = _items
        # set to None if properties (nullable) is None
        # and __fields_set__ contains the field
        if self.properties is None and "properties" in self.__fields_set__:
            _dict['properties'] = None

        # set to None if participation_type (nullable) is None
        # and __fields_set__ contains the field
        if self.participation_type is None and "participation_type" in self.__fields_set__:
            _dict['participationType'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> InstrumentEventHolder:
        """Create an instance of InstrumentEventHolder from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return InstrumentEventHolder.parse_obj(obj)

        _obj = InstrumentEventHolder.parse_obj({
            "instrument_event_id": obj.get("instrumentEventId"),
            "corporate_action_source_id": ResourceId.from_dict(obj.get("corporateActionSourceId")) if obj.get("corporateActionSourceId") is not None else None,
            "instrument_identifiers": obj.get("instrumentIdentifiers"),
            "lusid_instrument_id": obj.get("lusidInstrumentId"),
            "instrument_scope": obj.get("instrumentScope"),
            "description": obj.get("description"),
            "event_date_range": EventDateRange.from_dict(obj.get("eventDateRange")) if obj.get("eventDateRange") is not None else None,
            "instrument_event": InstrumentEvent.from_dict(obj.get("instrumentEvent")) if obj.get("instrumentEvent") is not None else None,
            "properties": [PerpetualProperty.from_dict(_item) for _item in obj.get("properties")] if obj.get("properties") is not None else None,
            "sequence_number": obj.get("sequenceNumber"),
            "participation_type": obj.get("participationType") if obj.get("participationType") is not None else 'Mandatory'
        })
        return _obj
