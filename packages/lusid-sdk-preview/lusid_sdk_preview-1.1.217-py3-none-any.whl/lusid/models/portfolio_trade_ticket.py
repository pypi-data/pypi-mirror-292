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


class PortfolioTradeTicket(object):
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
        'source_portfolio_id': 'ResourceId',
        'trade_ticket': 'LusidTradeTicket'
    }

    attribute_map = {
        'source_portfolio_id': 'sourcePortfolioId',
        'trade_ticket': 'tradeTicket'
    }

    required_map = {
        'source_portfolio_id': 'optional',
        'trade_ticket': 'optional'
    }

    def __init__(self, source_portfolio_id=None, trade_ticket=None, local_vars_configuration=None):  # noqa: E501
        """PortfolioTradeTicket - a model defined in OpenAPI"
        
        :param source_portfolio_id: 
        :type source_portfolio_id: lusid.ResourceId
        :param trade_ticket: 
        :type trade_ticket: lusid.LusidTradeTicket

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._source_portfolio_id = None
        self._trade_ticket = None
        self.discriminator = None

        if source_portfolio_id is not None:
            self.source_portfolio_id = source_portfolio_id
        if trade_ticket is not None:
            self.trade_ticket = trade_ticket

    @property
    def source_portfolio_id(self):
        """Gets the source_portfolio_id of this PortfolioTradeTicket.  # noqa: E501


        :return: The source_portfolio_id of this PortfolioTradeTicket.  # noqa: E501
        :rtype: lusid.ResourceId
        """
        return self._source_portfolio_id

    @source_portfolio_id.setter
    def source_portfolio_id(self, source_portfolio_id):
        """Sets the source_portfolio_id of this PortfolioTradeTicket.


        :param source_portfolio_id: The source_portfolio_id of this PortfolioTradeTicket.  # noqa: E501
        :type source_portfolio_id: lusid.ResourceId
        """

        self._source_portfolio_id = source_portfolio_id

    @property
    def trade_ticket(self):
        """Gets the trade_ticket of this PortfolioTradeTicket.  # noqa: E501


        :return: The trade_ticket of this PortfolioTradeTicket.  # noqa: E501
        :rtype: lusid.LusidTradeTicket
        """
        return self._trade_ticket

    @trade_ticket.setter
    def trade_ticket(self, trade_ticket):
        """Sets the trade_ticket of this PortfolioTradeTicket.


        :param trade_ticket: The trade_ticket of this PortfolioTradeTicket.  # noqa: E501
        :type trade_ticket: lusid.LusidTradeTicket
        """

        self._trade_ticket = trade_ticket

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
        if not isinstance(other, PortfolioTradeTicket):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, PortfolioTradeTicket):
            return True

        return self.to_dict() != other.to_dict()
