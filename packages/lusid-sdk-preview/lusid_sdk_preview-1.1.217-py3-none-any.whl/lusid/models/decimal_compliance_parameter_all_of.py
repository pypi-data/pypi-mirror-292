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


class DecimalComplianceParameterAllOf(object):
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
        'value': 'float',
        'compliance_parameter_type': 'str'
    }

    attribute_map = {
        'value': 'value',
        'compliance_parameter_type': 'complianceParameterType'
    }

    required_map = {
        'value': 'required',
        'compliance_parameter_type': 'required'
    }

    def __init__(self, value=None, compliance_parameter_type=None, local_vars_configuration=None):  # noqa: E501
        """DecimalComplianceParameterAllOf - a model defined in OpenAPI"
        
        :param value:  (required)
        :type value: float
        :param compliance_parameter_type:  The parameter type. The available values are: BoolComplianceParameter, StringComplianceParameter, DecimalComplianceParameter, DateTimeComplianceParameter, PropertyKeyComplianceParameter, AddressKeyComplianceParameter, PortfolioIdComplianceParameter, PortfolioGroupIdComplianceParameter, StringListComplianceParameter, BoolListComplianceParameter, DateTimeListComplianceParameter, DecimalListComplianceParameter, PropertyKeyListComplianceParameter, AddressKeyListComplianceParameter, PortfolioIdListComplianceParameter, PortfolioGroupIdListComplianceParameter, InstrumentListComplianceParameter, FilterPredicateComplianceParameter, GroupFilterPredicateComplianceParameter, GroupBySelectorComplianceParameter, PropertyListComplianceParameter, GroupCalculationComplianceParameter (required)
        :type compliance_parameter_type: str

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._value = None
        self._compliance_parameter_type = None
        self.discriminator = None

        self.value = value
        self.compliance_parameter_type = compliance_parameter_type

    @property
    def value(self):
        """Gets the value of this DecimalComplianceParameterAllOf.  # noqa: E501


        :return: The value of this DecimalComplianceParameterAllOf.  # noqa: E501
        :rtype: float
        """
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value of this DecimalComplianceParameterAllOf.


        :param value: The value of this DecimalComplianceParameterAllOf.  # noqa: E501
        :type value: float
        """
        if self.local_vars_configuration.client_side_validation and value is None:  # noqa: E501
            raise ValueError("Invalid value for `value`, must not be `None`")  # noqa: E501

        self._value = value

    @property
    def compliance_parameter_type(self):
        """Gets the compliance_parameter_type of this DecimalComplianceParameterAllOf.  # noqa: E501

        The parameter type. The available values are: BoolComplianceParameter, StringComplianceParameter, DecimalComplianceParameter, DateTimeComplianceParameter, PropertyKeyComplianceParameter, AddressKeyComplianceParameter, PortfolioIdComplianceParameter, PortfolioGroupIdComplianceParameter, StringListComplianceParameter, BoolListComplianceParameter, DateTimeListComplianceParameter, DecimalListComplianceParameter, PropertyKeyListComplianceParameter, AddressKeyListComplianceParameter, PortfolioIdListComplianceParameter, PortfolioGroupIdListComplianceParameter, InstrumentListComplianceParameter, FilterPredicateComplianceParameter, GroupFilterPredicateComplianceParameter, GroupBySelectorComplianceParameter, PropertyListComplianceParameter, GroupCalculationComplianceParameter  # noqa: E501

        :return: The compliance_parameter_type of this DecimalComplianceParameterAllOf.  # noqa: E501
        :rtype: str
        """
        return self._compliance_parameter_type

    @compliance_parameter_type.setter
    def compliance_parameter_type(self, compliance_parameter_type):
        """Sets the compliance_parameter_type of this DecimalComplianceParameterAllOf.

        The parameter type. The available values are: BoolComplianceParameter, StringComplianceParameter, DecimalComplianceParameter, DateTimeComplianceParameter, PropertyKeyComplianceParameter, AddressKeyComplianceParameter, PortfolioIdComplianceParameter, PortfolioGroupIdComplianceParameter, StringListComplianceParameter, BoolListComplianceParameter, DateTimeListComplianceParameter, DecimalListComplianceParameter, PropertyKeyListComplianceParameter, AddressKeyListComplianceParameter, PortfolioIdListComplianceParameter, PortfolioGroupIdListComplianceParameter, InstrumentListComplianceParameter, FilterPredicateComplianceParameter, GroupFilterPredicateComplianceParameter, GroupBySelectorComplianceParameter, PropertyListComplianceParameter, GroupCalculationComplianceParameter  # noqa: E501

        :param compliance_parameter_type: The compliance_parameter_type of this DecimalComplianceParameterAllOf.  # noqa: E501
        :type compliance_parameter_type: str
        """
        if self.local_vars_configuration.client_side_validation and compliance_parameter_type is None:  # noqa: E501
            raise ValueError("Invalid value for `compliance_parameter_type`, must not be `None`")  # noqa: E501
        allowed_values = ["BoolComplianceParameter", "StringComplianceParameter", "DecimalComplianceParameter", "DateTimeComplianceParameter", "PropertyKeyComplianceParameter", "AddressKeyComplianceParameter", "PortfolioIdComplianceParameter", "PortfolioGroupIdComplianceParameter", "StringListComplianceParameter", "BoolListComplianceParameter", "DateTimeListComplianceParameter", "DecimalListComplianceParameter", "PropertyKeyListComplianceParameter", "AddressKeyListComplianceParameter", "PortfolioIdListComplianceParameter", "PortfolioGroupIdListComplianceParameter", "InstrumentListComplianceParameter", "FilterPredicateComplianceParameter", "GroupFilterPredicateComplianceParameter", "GroupBySelectorComplianceParameter", "PropertyListComplianceParameter", "GroupCalculationComplianceParameter"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and compliance_parameter_type not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `compliance_parameter_type` ({0}), must be one of {1}"  # noqa: E501
                .format(compliance_parameter_type, allowed_values)
            )

        self._compliance_parameter_type = compliance_parameter_type

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
        if not isinstance(other, DecimalComplianceParameterAllOf):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DecimalComplianceParameterAllOf):
            return True

        return self.to_dict() != other.to_dict()
