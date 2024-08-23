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


class FlowConventionName(object):
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
        'currency': 'str',
        'index_name': 'str',
        'tenor': 'str'
    }

    attribute_map = {
        'currency': 'currency',
        'index_name': 'indexName',
        'tenor': 'tenor'
    }

    required_map = {
        'currency': 'required',
        'index_name': 'optional',
        'tenor': 'required'
    }

    def __init__(self, currency=None, index_name=None, tenor=None, local_vars_configuration=None):  # noqa: E501
        """FlowConventionName - a model defined in OpenAPI"
        
        :param currency:  Currency of the flow convention name. (required)
        :type currency: str
        :param index_name:  The index, if present, that is required. e.g. \"IBOR\", \"OIS\" or \"SONIA\".
        :type index_name: str
        :param tenor:  Tenor for the convention name.    For more information on tenors, see [knowledge base article KA-02097](https://support.lusid.com/knowledgebase/article/KA-02097) (required)
        :type tenor: str

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._currency = None
        self._index_name = None
        self._tenor = None
        self.discriminator = None

        self.currency = currency
        self.index_name = index_name
        self.tenor = tenor

    @property
    def currency(self):
        """Gets the currency of this FlowConventionName.  # noqa: E501

        Currency of the flow convention name.  # noqa: E501

        :return: The currency of this FlowConventionName.  # noqa: E501
        :rtype: str
        """
        return self._currency

    @currency.setter
    def currency(self, currency):
        """Sets the currency of this FlowConventionName.

        Currency of the flow convention name.  # noqa: E501

        :param currency: The currency of this FlowConventionName.  # noqa: E501
        :type currency: str
        """
        if self.local_vars_configuration.client_side_validation and currency is None:  # noqa: E501
            raise ValueError("Invalid value for `currency`, must not be `None`")  # noqa: E501

        self._currency = currency

    @property
    def index_name(self):
        """Gets the index_name of this FlowConventionName.  # noqa: E501

        The index, if present, that is required. e.g. \"IBOR\", \"OIS\" or \"SONIA\".  # noqa: E501

        :return: The index_name of this FlowConventionName.  # noqa: E501
        :rtype: str
        """
        return self._index_name

    @index_name.setter
    def index_name(self, index_name):
        """Sets the index_name of this FlowConventionName.

        The index, if present, that is required. e.g. \"IBOR\", \"OIS\" or \"SONIA\".  # noqa: E501

        :param index_name: The index_name of this FlowConventionName.  # noqa: E501
        :type index_name: str
        """

        self._index_name = index_name

    @property
    def tenor(self):
        """Gets the tenor of this FlowConventionName.  # noqa: E501

        Tenor for the convention name.    For more information on tenors, see [knowledge base article KA-02097](https://support.lusid.com/knowledgebase/article/KA-02097)  # noqa: E501

        :return: The tenor of this FlowConventionName.  # noqa: E501
        :rtype: str
        """
        return self._tenor

    @tenor.setter
    def tenor(self, tenor):
        """Sets the tenor of this FlowConventionName.

        Tenor for the convention name.    For more information on tenors, see [knowledge base article KA-02097](https://support.lusid.com/knowledgebase/article/KA-02097)  # noqa: E501

        :param tenor: The tenor of this FlowConventionName.  # noqa: E501
        :type tenor: str
        """
        if self.local_vars_configuration.client_side_validation and tenor is None:  # noqa: E501
            raise ValueError("Invalid value for `tenor`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                tenor is not None and len(tenor) < 1):
            raise ValueError("Invalid value for `tenor`, length must be greater than or equal to `1`")  # noqa: E501

        self._tenor = tenor

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
        if not isinstance(other, FlowConventionName):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FlowConventionName):
            return True

        return self.to_dict() != other.to_dict()
