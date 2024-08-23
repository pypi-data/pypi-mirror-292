# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 1.1.217
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
import pprint
import re  # noqa: F401
import six

from lusid.configuration import Configuration


class CancelledPlacementResult(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
      required_map (dict): The key is attribute name
                           and the value is whether it is 'required' or 'optional'.
    """
    openapi_types = {
        'placement_state': 'Placement',
        'cancelled_child_placements': 'list[ResourceId]'
    }

    attribute_map = {
        'placement_state': 'placementState',
        'cancelled_child_placements': 'cancelledChildPlacements'
    }

    required_map = {
        'placement_state': 'optional',
        'cancelled_child_placements': 'required'
    }

    def __init__(self, placement_state=None, cancelled_child_placements=None, local_vars_configuration=None):  # noqa: E501
        """CancelledPlacementResult - a model defined in OpenAPI"
        
        :param placement_state: 
        :type placement_state: lusid.Placement
        :param cancelled_child_placements:  Child placements which have also been cancelled following cancellation of the parent (required)
        :type cancelled_child_placements: list[lusid.ResourceId]

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._placement_state = None
        self._cancelled_child_placements = None
        self.discriminator = None

        if placement_state is not None:
            self.placement_state = placement_state
        self.cancelled_child_placements = cancelled_child_placements

    @property
    def placement_state(self):
        """Gets the placement_state of this CancelledPlacementResult.  # noqa: E501


        :return: The placement_state of this CancelledPlacementResult.  # noqa: E501
        :rtype: lusid.Placement
        """
        return self._placement_state

    @placement_state.setter
    def placement_state(self, placement_state):
        """Sets the placement_state of this CancelledPlacementResult.


        :param placement_state: The placement_state of this CancelledPlacementResult.  # noqa: E501
        :type placement_state: lusid.Placement
        """

        self._placement_state = placement_state

    @property
    def cancelled_child_placements(self):
        """Gets the cancelled_child_placements of this CancelledPlacementResult.  # noqa: E501

        Child placements which have also been cancelled following cancellation of the parent  # noqa: E501

        :return: The cancelled_child_placements of this CancelledPlacementResult.  # noqa: E501
        :rtype: list[lusid.ResourceId]
        """
        return self._cancelled_child_placements

    @cancelled_child_placements.setter
    def cancelled_child_placements(self, cancelled_child_placements):
        """Sets the cancelled_child_placements of this CancelledPlacementResult.

        Child placements which have also been cancelled following cancellation of the parent  # noqa: E501

        :param cancelled_child_placements: The cancelled_child_placements of this CancelledPlacementResult.  # noqa: E501
        :type cancelled_child_placements: list[lusid.ResourceId]
        """
        if self.local_vars_configuration.client_side_validation and cancelled_child_placements is None:  # noqa: E501
            raise ValueError("Invalid value for `cancelled_child_placements`, must not be `None`")  # noqa: E501

        self._cancelled_child_placements = cancelled_child_placements

    def to_dict(self, serialize=False):
        """Returns the model properties as a dict"""
        result = {}

        def convert(x):
            if hasattr(x, "to_dict"):
                args = getfullargspec(x.to_dict).args
                if len(args) == 1:
                    return x.to_dict()
                else:
                    return x.to_dict(serialize)
            else:
                return x

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            attr = self.attribute_map.get(attr, attr) if serialize else attr
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: convert(x),
                    value
                ))
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], convert(item[1])),
                    value.items()
                ))
            else:
                result[attr] = convert(value)

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, CancelledPlacementResult):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CancelledPlacementResult):
            return True

        return self.to_dict() != other.to_dict()
