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


class PreviousShareClassBreakdown(object):
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
        'nav': 'PreviousNAV',
        'unitisation': 'UnitisationData',
        'share_class_to_fund_fx_rate': 'float'
    }

    attribute_map = {
        'nav': 'nav',
        'unitisation': 'unitisation',
        'share_class_to_fund_fx_rate': 'shareClassToFundFxRate'
    }

    required_map = {
        'nav': 'required',
        'unitisation': 'optional',
        'share_class_to_fund_fx_rate': 'required'
    }

    def __init__(self, nav=None, unitisation=None, share_class_to_fund_fx_rate=None, local_vars_configuration=None):  # noqa: E501
        """PreviousShareClassBreakdown - a model defined in OpenAPI"
        
        :param nav:  (required)
        :type nav: lusid.PreviousNAV
        :param unitisation: 
        :type unitisation: lusid.UnitisationData
        :param share_class_to_fund_fx_rate:  The fx rate from the Share Class currency to the fund currency at this valuation point. (required)
        :type share_class_to_fund_fx_rate: float

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._nav = None
        self._unitisation = None
        self._share_class_to_fund_fx_rate = None
        self.discriminator = None

        self.nav = nav
        if unitisation is not None:
            self.unitisation = unitisation
        self.share_class_to_fund_fx_rate = share_class_to_fund_fx_rate

    @property
    def nav(self):
        """Gets the nav of this PreviousShareClassBreakdown.  # noqa: E501


        :return: The nav of this PreviousShareClassBreakdown.  # noqa: E501
        :rtype: lusid.PreviousNAV
        """
        return self._nav

    @nav.setter
    def nav(self, nav):
        """Sets the nav of this PreviousShareClassBreakdown.


        :param nav: The nav of this PreviousShareClassBreakdown.  # noqa: E501
        :type nav: lusid.PreviousNAV
        """
        if self.local_vars_configuration.client_side_validation and nav is None:  # noqa: E501
            raise ValueError("Invalid value for `nav`, must not be `None`")  # noqa: E501

        self._nav = nav

    @property
    def unitisation(self):
        """Gets the unitisation of this PreviousShareClassBreakdown.  # noqa: E501


        :return: The unitisation of this PreviousShareClassBreakdown.  # noqa: E501
        :rtype: lusid.UnitisationData
        """
        return self._unitisation

    @unitisation.setter
    def unitisation(self, unitisation):
        """Sets the unitisation of this PreviousShareClassBreakdown.


        :param unitisation: The unitisation of this PreviousShareClassBreakdown.  # noqa: E501
        :type unitisation: lusid.UnitisationData
        """

        self._unitisation = unitisation

    @property
    def share_class_to_fund_fx_rate(self):
        """Gets the share_class_to_fund_fx_rate of this PreviousShareClassBreakdown.  # noqa: E501

        The fx rate from the Share Class currency to the fund currency at this valuation point.  # noqa: E501

        :return: The share_class_to_fund_fx_rate of this PreviousShareClassBreakdown.  # noqa: E501
        :rtype: float
        """
        return self._share_class_to_fund_fx_rate

    @share_class_to_fund_fx_rate.setter
    def share_class_to_fund_fx_rate(self, share_class_to_fund_fx_rate):
        """Sets the share_class_to_fund_fx_rate of this PreviousShareClassBreakdown.

        The fx rate from the Share Class currency to the fund currency at this valuation point.  # noqa: E501

        :param share_class_to_fund_fx_rate: The share_class_to_fund_fx_rate of this PreviousShareClassBreakdown.  # noqa: E501
        :type share_class_to_fund_fx_rate: float
        """
        if self.local_vars_configuration.client_side_validation and share_class_to_fund_fx_rate is None:  # noqa: E501
            raise ValueError("Invalid value for `share_class_to_fund_fx_rate`, must not be `None`")  # noqa: E501

        self._share_class_to_fund_fx_rate = share_class_to_fund_fx_rate

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
        if not isinstance(other, PreviousShareClassBreakdown):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, PreviousShareClassBreakdown):
            return True

        return self.to_dict() != other.to_dict()
