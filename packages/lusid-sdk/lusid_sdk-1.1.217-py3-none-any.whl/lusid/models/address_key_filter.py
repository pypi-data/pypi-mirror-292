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


class AddressKeyFilter(object):
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
        'left': 'str',
        'operator': 'str',
        'right': 'ResultValue'
    }

    attribute_map = {
        'left': 'left',
        'operator': 'operator',
        'right': 'right'
    }

    required_map = {
        'left': 'optional',
        'operator': 'optional',
        'right': 'optional'
    }

    def __init__(self, left=None, operator=None, right=None, local_vars_configuration=None):  # noqa: E501
        """AddressKeyFilter - a model defined in OpenAPI"
        
        :param left:  Address for the value in the row
        :type left: str
        :param operator:  What sort of comparison is the filter performing. Can be either \"eq\" for equals or \"neq\" for not equals.
        :type operator: str
        :param right: 
        :type right: lusid.ResultValue

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._left = None
        self._operator = None
        self._right = None
        self.discriminator = None

        self.left = left
        self.operator = operator
        if right is not None:
            self.right = right

    @property
    def left(self):
        """Gets the left of this AddressKeyFilter.  # noqa: E501

        Address for the value in the row  # noqa: E501

        :return: The left of this AddressKeyFilter.  # noqa: E501
        :rtype: str
        """
        return self._left

    @left.setter
    def left(self, left):
        """Sets the left of this AddressKeyFilter.

        Address for the value in the row  # noqa: E501

        :param left: The left of this AddressKeyFilter.  # noqa: E501
        :type left: str
        """

        self._left = left

    @property
    def operator(self):
        """Gets the operator of this AddressKeyFilter.  # noqa: E501

        What sort of comparison is the filter performing. Can be either \"eq\" for equals or \"neq\" for not equals.  # noqa: E501

        :return: The operator of this AddressKeyFilter.  # noqa: E501
        :rtype: str
        """
        return self._operator

    @operator.setter
    def operator(self, operator):
        """Sets the operator of this AddressKeyFilter.

        What sort of comparison is the filter performing. Can be either \"eq\" for equals or \"neq\" for not equals.  # noqa: E501

        :param operator: The operator of this AddressKeyFilter.  # noqa: E501
        :type operator: str
        """
        if (self.local_vars_configuration.client_side_validation and
                operator is not None and len(operator) > 3):
            raise ValueError("Invalid value for `operator`, length must be less than or equal to `3`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                operator is not None and len(operator) < 0):
            raise ValueError("Invalid value for `operator`, length must be greater than or equal to `0`")  # noqa: E501

        self._operator = operator

    @property
    def right(self):
        """Gets the right of this AddressKeyFilter.  # noqa: E501


        :return: The right of this AddressKeyFilter.  # noqa: E501
        :rtype: lusid.ResultValue
        """
        return self._right

    @right.setter
    def right(self, right):
        """Sets the right of this AddressKeyFilter.


        :param right: The right of this AddressKeyFilter.  # noqa: E501
        :type right: lusid.ResultValue
        """

        self._right = right

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
        if not isinstance(other, AddressKeyFilter):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AddressKeyFilter):
            return True

        return self.to_dict() != other.to_dict()
