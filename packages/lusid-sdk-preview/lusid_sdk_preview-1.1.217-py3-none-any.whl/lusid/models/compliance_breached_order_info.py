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


class ComplianceBreachedOrderInfo(object):
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
        'order_id': 'ResourceId',
        'list_rule_result': 'list[ComplianceRuleResult]'
    }

    attribute_map = {
        'order_id': 'orderId',
        'list_rule_result': 'listRuleResult'
    }

    required_map = {
        'order_id': 'required',
        'list_rule_result': 'required'
    }

    def __init__(self, order_id=None, list_rule_result=None, local_vars_configuration=None):  # noqa: E501
        """ComplianceBreachedOrderInfo - a model defined in OpenAPI"
        
        :param order_id:  (required)
        :type order_id: lusid.ResourceId
        :param list_rule_result:  The Rule Results for a particular compliance run (required)
        :type list_rule_result: list[lusid.ComplianceRuleResult]

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._order_id = None
        self._list_rule_result = None
        self.discriminator = None

        self.order_id = order_id
        self.list_rule_result = list_rule_result

    @property
    def order_id(self):
        """Gets the order_id of this ComplianceBreachedOrderInfo.  # noqa: E501


        :return: The order_id of this ComplianceBreachedOrderInfo.  # noqa: E501
        :rtype: lusid.ResourceId
        """
        return self._order_id

    @order_id.setter
    def order_id(self, order_id):
        """Sets the order_id of this ComplianceBreachedOrderInfo.


        :param order_id: The order_id of this ComplianceBreachedOrderInfo.  # noqa: E501
        :type order_id: lusid.ResourceId
        """
        if self.local_vars_configuration.client_side_validation and order_id is None:  # noqa: E501
            raise ValueError("Invalid value for `order_id`, must not be `None`")  # noqa: E501

        self._order_id = order_id

    @property
    def list_rule_result(self):
        """Gets the list_rule_result of this ComplianceBreachedOrderInfo.  # noqa: E501

        The Rule Results for a particular compliance run  # noqa: E501

        :return: The list_rule_result of this ComplianceBreachedOrderInfo.  # noqa: E501
        :rtype: list[lusid.ComplianceRuleResult]
        """
        return self._list_rule_result

    @list_rule_result.setter
    def list_rule_result(self, list_rule_result):
        """Sets the list_rule_result of this ComplianceBreachedOrderInfo.

        The Rule Results for a particular compliance run  # noqa: E501

        :param list_rule_result: The list_rule_result of this ComplianceBreachedOrderInfo.  # noqa: E501
        :type list_rule_result: list[lusid.ComplianceRuleResult]
        """
        if self.local_vars_configuration.client_side_validation and list_rule_result is None:  # noqa: E501
            raise ValueError("Invalid value for `list_rule_result`, must not be `None`")  # noqa: E501

        self._list_rule_result = list_rule_result

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
        if not isinstance(other, ComplianceBreachedOrderInfo):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ComplianceBreachedOrderInfo):
            return True

        return self.to_dict() != other.to_dict()
