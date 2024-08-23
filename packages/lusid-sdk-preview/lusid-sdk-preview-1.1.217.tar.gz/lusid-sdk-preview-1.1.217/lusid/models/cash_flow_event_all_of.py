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


class CashFlowEventAllOf(object):
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
        'cash_flow_value': 'CashFlowValue',
        'event_type': 'str',
        'instrument_event_type': 'str'
    }

    attribute_map = {
        'cash_flow_value': 'cashFlowValue',
        'event_type': 'eventType',
        'instrument_event_type': 'instrumentEventType'
    }

    required_map = {
        'cash_flow_value': 'required',
        'event_type': 'required',
        'instrument_event_type': 'required'
    }

    def __init__(self, cash_flow_value=None, event_type=None, instrument_event_type=None, local_vars_configuration=None):  # noqa: E501
        """CashFlowEventAllOf - a model defined in OpenAPI"
        
        :param cash_flow_value:  (required)
        :type cash_flow_value: lusid.CashFlowValue
        :param event_type:  What type of internal event does this represent; coupon, principal, premium etc. (required)
        :type event_type: str
        :param instrument_event_type:  The Type of Event. The available values are: TransitionEvent, InformationalEvent, OpenEvent, CloseEvent, StockSplitEvent, BondDefaultEvent, CashDividendEvent, AmortisationEvent, CashFlowEvent, ExerciseEvent, ResetEvent, TriggerEvent, RawVendorEvent, InformationalErrorEvent, BondCouponEvent, DividendReinvestmentEvent, AccumulationEvent, BondPrincipalEvent, DividendOptionEvent, MaturityEvent, FxForwardSettlementEvent, ExpiryEvent, ScripDividendEvent, StockDividendEvent, ReverseStockSplitEvent, CapitalDistributionEvent, SpinOffEvent, MergerEvent, FutureExpiryEvent, SwapCashFlowEvent, SwapPrincipalEvent (required)
        :type instrument_event_type: str

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._cash_flow_value = None
        self._event_type = None
        self._instrument_event_type = None
        self.discriminator = None

        self.cash_flow_value = cash_flow_value
        self.event_type = event_type
        self.instrument_event_type = instrument_event_type

    @property
    def cash_flow_value(self):
        """Gets the cash_flow_value of this CashFlowEventAllOf.  # noqa: E501


        :return: The cash_flow_value of this CashFlowEventAllOf.  # noqa: E501
        :rtype: lusid.CashFlowValue
        """
        return self._cash_flow_value

    @cash_flow_value.setter
    def cash_flow_value(self, cash_flow_value):
        """Sets the cash_flow_value of this CashFlowEventAllOf.


        :param cash_flow_value: The cash_flow_value of this CashFlowEventAllOf.  # noqa: E501
        :type cash_flow_value: lusid.CashFlowValue
        """
        if self.local_vars_configuration.client_side_validation and cash_flow_value is None:  # noqa: E501
            raise ValueError("Invalid value for `cash_flow_value`, must not be `None`")  # noqa: E501

        self._cash_flow_value = cash_flow_value

    @property
    def event_type(self):
        """Gets the event_type of this CashFlowEventAllOf.  # noqa: E501

        What type of internal event does this represent; coupon, principal, premium etc.  # noqa: E501

        :return: The event_type of this CashFlowEventAllOf.  # noqa: E501
        :rtype: str
        """
        return self._event_type

    @event_type.setter
    def event_type(self, event_type):
        """Sets the event_type of this CashFlowEventAllOf.

        What type of internal event does this represent; coupon, principal, premium etc.  # noqa: E501

        :param event_type: The event_type of this CashFlowEventAllOf.  # noqa: E501
        :type event_type: str
        """
        if self.local_vars_configuration.client_side_validation and event_type is None:  # noqa: E501
            raise ValueError("Invalid value for `event_type`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                event_type is not None and len(event_type) < 1):
            raise ValueError("Invalid value for `event_type`, length must be greater than or equal to `1`")  # noqa: E501

        self._event_type = event_type

    @property
    def instrument_event_type(self):
        """Gets the instrument_event_type of this CashFlowEventAllOf.  # noqa: E501

        The Type of Event. The available values are: TransitionEvent, InformationalEvent, OpenEvent, CloseEvent, StockSplitEvent, BondDefaultEvent, CashDividendEvent, AmortisationEvent, CashFlowEvent, ExerciseEvent, ResetEvent, TriggerEvent, RawVendorEvent, InformationalErrorEvent, BondCouponEvent, DividendReinvestmentEvent, AccumulationEvent, BondPrincipalEvent, DividendOptionEvent, MaturityEvent, FxForwardSettlementEvent, ExpiryEvent, ScripDividendEvent, StockDividendEvent, ReverseStockSplitEvent, CapitalDistributionEvent, SpinOffEvent, MergerEvent, FutureExpiryEvent, SwapCashFlowEvent, SwapPrincipalEvent  # noqa: E501

        :return: The instrument_event_type of this CashFlowEventAllOf.  # noqa: E501
        :rtype: str
        """
        return self._instrument_event_type

    @instrument_event_type.setter
    def instrument_event_type(self, instrument_event_type):
        """Sets the instrument_event_type of this CashFlowEventAllOf.

        The Type of Event. The available values are: TransitionEvent, InformationalEvent, OpenEvent, CloseEvent, StockSplitEvent, BondDefaultEvent, CashDividendEvent, AmortisationEvent, CashFlowEvent, ExerciseEvent, ResetEvent, TriggerEvent, RawVendorEvent, InformationalErrorEvent, BondCouponEvent, DividendReinvestmentEvent, AccumulationEvent, BondPrincipalEvent, DividendOptionEvent, MaturityEvent, FxForwardSettlementEvent, ExpiryEvent, ScripDividendEvent, StockDividendEvent, ReverseStockSplitEvent, CapitalDistributionEvent, SpinOffEvent, MergerEvent, FutureExpiryEvent, SwapCashFlowEvent, SwapPrincipalEvent  # noqa: E501

        :param instrument_event_type: The instrument_event_type of this CashFlowEventAllOf.  # noqa: E501
        :type instrument_event_type: str
        """
        if self.local_vars_configuration.client_side_validation and instrument_event_type is None:  # noqa: E501
            raise ValueError("Invalid value for `instrument_event_type`, must not be `None`")  # noqa: E501
        allowed_values = ["TransitionEvent", "InformationalEvent", "OpenEvent", "CloseEvent", "StockSplitEvent", "BondDefaultEvent", "CashDividendEvent", "AmortisationEvent", "CashFlowEvent", "ExerciseEvent", "ResetEvent", "TriggerEvent", "RawVendorEvent", "InformationalErrorEvent", "BondCouponEvent", "DividendReinvestmentEvent", "AccumulationEvent", "BondPrincipalEvent", "DividendOptionEvent", "MaturityEvent", "FxForwardSettlementEvent", "ExpiryEvent", "ScripDividendEvent", "StockDividendEvent", "ReverseStockSplitEvent", "CapitalDistributionEvent", "SpinOffEvent", "MergerEvent", "FutureExpiryEvent", "SwapCashFlowEvent", "SwapPrincipalEvent"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and instrument_event_type not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `instrument_event_type` ({0}), must be one of {1}"  # noqa: E501
                .format(instrument_event_type, allowed_values)
            )

        self._instrument_event_type = instrument_event_type

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
        if not isinstance(other, CashFlowEventAllOf):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CashFlowEventAllOf):
            return True

        return self.to_dict() != other.to_dict()
