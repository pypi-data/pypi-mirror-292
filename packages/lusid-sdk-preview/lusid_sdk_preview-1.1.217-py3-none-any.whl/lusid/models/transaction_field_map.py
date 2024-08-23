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


class TransactionFieldMap(object):
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
        'transaction_id': 'str',
        'type': 'str',
        'source': 'str',
        'instrument': 'str',
        'transaction_date': 'str',
        'settlement_date': 'str',
        'units': 'str',
        'transaction_price': 'TransactionPriceAndType',
        'transaction_currency': 'str',
        'exchange_rate': 'str',
        'total_consideration': 'TransactionCurrencyAndAmount'
    }

    attribute_map = {
        'transaction_id': 'transactionId',
        'type': 'type',
        'source': 'source',
        'instrument': 'instrument',
        'transaction_date': 'transactionDate',
        'settlement_date': 'settlementDate',
        'units': 'units',
        'transaction_price': 'transactionPrice',
        'transaction_currency': 'transactionCurrency',
        'exchange_rate': 'exchangeRate',
        'total_consideration': 'totalConsideration'
    }

    required_map = {
        'transaction_id': 'required',
        'type': 'required',
        'source': 'required',
        'instrument': 'required',
        'transaction_date': 'required',
        'settlement_date': 'required',
        'units': 'required',
        'transaction_price': 'optional',
        'transaction_currency': 'required',
        'exchange_rate': 'optional',
        'total_consideration': 'required'
    }

    def __init__(self, transaction_id=None, type=None, source=None, instrument=None, transaction_date=None, settlement_date=None, units=None, transaction_price=None, transaction_currency=None, exchange_rate=None, total_consideration=None, local_vars_configuration=None):  # noqa: E501
        """TransactionFieldMap - a model defined in OpenAPI"
        
        :param transaction_id:  (required)
        :type transaction_id: str
        :param type:  (required)
        :type type: str
        :param source:  (required)
        :type source: str
        :param instrument:  (required)
        :type instrument: str
        :param transaction_date:  (required)
        :type transaction_date: str
        :param settlement_date:  (required)
        :type settlement_date: str
        :param units:  (required)
        :type units: str
        :param transaction_price: 
        :type transaction_price: lusid.TransactionPriceAndType
        :param transaction_currency:  (required)
        :type transaction_currency: str
        :param exchange_rate: 
        :type exchange_rate: str
        :param total_consideration:  (required)
        :type total_consideration: lusid.TransactionCurrencyAndAmount

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._transaction_id = None
        self._type = None
        self._source = None
        self._instrument = None
        self._transaction_date = None
        self._settlement_date = None
        self._units = None
        self._transaction_price = None
        self._transaction_currency = None
        self._exchange_rate = None
        self._total_consideration = None
        self.discriminator = None

        self.transaction_id = transaction_id
        self.type = type
        self.source = source
        self.instrument = instrument
        self.transaction_date = transaction_date
        self.settlement_date = settlement_date
        self.units = units
        if transaction_price is not None:
            self.transaction_price = transaction_price
        self.transaction_currency = transaction_currency
        self.exchange_rate = exchange_rate
        self.total_consideration = total_consideration

    @property
    def transaction_id(self):
        """Gets the transaction_id of this TransactionFieldMap.  # noqa: E501


        :return: The transaction_id of this TransactionFieldMap.  # noqa: E501
        :rtype: str
        """
        return self._transaction_id

    @transaction_id.setter
    def transaction_id(self, transaction_id):
        """Sets the transaction_id of this TransactionFieldMap.


        :param transaction_id: The transaction_id of this TransactionFieldMap.  # noqa: E501
        :type transaction_id: str
        """
        if self.local_vars_configuration.client_side_validation and transaction_id is None:  # noqa: E501
            raise ValueError("Invalid value for `transaction_id`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                transaction_id is not None and len(transaction_id) > 1024):
            raise ValueError("Invalid value for `transaction_id`, length must be less than or equal to `1024`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                transaction_id is not None and len(transaction_id) < 0):
            raise ValueError("Invalid value for `transaction_id`, length must be greater than or equal to `0`")  # noqa: E501

        self._transaction_id = transaction_id

    @property
    def type(self):
        """Gets the type of this TransactionFieldMap.  # noqa: E501


        :return: The type of this TransactionFieldMap.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this TransactionFieldMap.


        :param type: The type of this TransactionFieldMap.  # noqa: E501
        :type type: str
        """
        if self.local_vars_configuration.client_side_validation and type is None:  # noqa: E501
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                type is not None and len(type) > 1024):
            raise ValueError("Invalid value for `type`, length must be less than or equal to `1024`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                type is not None and len(type) < 0):
            raise ValueError("Invalid value for `type`, length must be greater than or equal to `0`")  # noqa: E501

        self._type = type

    @property
    def source(self):
        """Gets the source of this TransactionFieldMap.  # noqa: E501


        :return: The source of this TransactionFieldMap.  # noqa: E501
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source):
        """Sets the source of this TransactionFieldMap.


        :param source: The source of this TransactionFieldMap.  # noqa: E501
        :type source: str
        """
        if self.local_vars_configuration.client_side_validation and source is None:  # noqa: E501
            raise ValueError("Invalid value for `source`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                source is not None and len(source) > 1024):
            raise ValueError("Invalid value for `source`, length must be less than or equal to `1024`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                source is not None and len(source) < 0):
            raise ValueError("Invalid value for `source`, length must be greater than or equal to `0`")  # noqa: E501

        self._source = source

    @property
    def instrument(self):
        """Gets the instrument of this TransactionFieldMap.  # noqa: E501


        :return: The instrument of this TransactionFieldMap.  # noqa: E501
        :rtype: str
        """
        return self._instrument

    @instrument.setter
    def instrument(self, instrument):
        """Sets the instrument of this TransactionFieldMap.


        :param instrument: The instrument of this TransactionFieldMap.  # noqa: E501
        :type instrument: str
        """
        if self.local_vars_configuration.client_side_validation and instrument is None:  # noqa: E501
            raise ValueError("Invalid value for `instrument`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                instrument is not None and len(instrument) > 1024):
            raise ValueError("Invalid value for `instrument`, length must be less than or equal to `1024`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                instrument is not None and len(instrument) < 0):
            raise ValueError("Invalid value for `instrument`, length must be greater than or equal to `0`")  # noqa: E501

        self._instrument = instrument

    @property
    def transaction_date(self):
        """Gets the transaction_date of this TransactionFieldMap.  # noqa: E501


        :return: The transaction_date of this TransactionFieldMap.  # noqa: E501
        :rtype: str
        """
        return self._transaction_date

    @transaction_date.setter
    def transaction_date(self, transaction_date):
        """Sets the transaction_date of this TransactionFieldMap.


        :param transaction_date: The transaction_date of this TransactionFieldMap.  # noqa: E501
        :type transaction_date: str
        """
        if self.local_vars_configuration.client_side_validation and transaction_date is None:  # noqa: E501
            raise ValueError("Invalid value for `transaction_date`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                transaction_date is not None and len(transaction_date) > 1024):
            raise ValueError("Invalid value for `transaction_date`, length must be less than or equal to `1024`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                transaction_date is not None and len(transaction_date) < 0):
            raise ValueError("Invalid value for `transaction_date`, length must be greater than or equal to `0`")  # noqa: E501

        self._transaction_date = transaction_date

    @property
    def settlement_date(self):
        """Gets the settlement_date of this TransactionFieldMap.  # noqa: E501


        :return: The settlement_date of this TransactionFieldMap.  # noqa: E501
        :rtype: str
        """
        return self._settlement_date

    @settlement_date.setter
    def settlement_date(self, settlement_date):
        """Sets the settlement_date of this TransactionFieldMap.


        :param settlement_date: The settlement_date of this TransactionFieldMap.  # noqa: E501
        :type settlement_date: str
        """
        if self.local_vars_configuration.client_side_validation and settlement_date is None:  # noqa: E501
            raise ValueError("Invalid value for `settlement_date`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                settlement_date is not None and len(settlement_date) > 1024):
            raise ValueError("Invalid value for `settlement_date`, length must be less than or equal to `1024`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                settlement_date is not None and len(settlement_date) < 0):
            raise ValueError("Invalid value for `settlement_date`, length must be greater than or equal to `0`")  # noqa: E501

        self._settlement_date = settlement_date

    @property
    def units(self):
        """Gets the units of this TransactionFieldMap.  # noqa: E501


        :return: The units of this TransactionFieldMap.  # noqa: E501
        :rtype: str
        """
        return self._units

    @units.setter
    def units(self, units):
        """Sets the units of this TransactionFieldMap.


        :param units: The units of this TransactionFieldMap.  # noqa: E501
        :type units: str
        """
        if self.local_vars_configuration.client_side_validation and units is None:  # noqa: E501
            raise ValueError("Invalid value for `units`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                units is not None and len(units) > 1024):
            raise ValueError("Invalid value for `units`, length must be less than or equal to `1024`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                units is not None and len(units) < 0):
            raise ValueError("Invalid value for `units`, length must be greater than or equal to `0`")  # noqa: E501

        self._units = units

    @property
    def transaction_price(self):
        """Gets the transaction_price of this TransactionFieldMap.  # noqa: E501


        :return: The transaction_price of this TransactionFieldMap.  # noqa: E501
        :rtype: lusid.TransactionPriceAndType
        """
        return self._transaction_price

    @transaction_price.setter
    def transaction_price(self, transaction_price):
        """Sets the transaction_price of this TransactionFieldMap.


        :param transaction_price: The transaction_price of this TransactionFieldMap.  # noqa: E501
        :type transaction_price: lusid.TransactionPriceAndType
        """

        self._transaction_price = transaction_price

    @property
    def transaction_currency(self):
        """Gets the transaction_currency of this TransactionFieldMap.  # noqa: E501


        :return: The transaction_currency of this TransactionFieldMap.  # noqa: E501
        :rtype: str
        """
        return self._transaction_currency

    @transaction_currency.setter
    def transaction_currency(self, transaction_currency):
        """Sets the transaction_currency of this TransactionFieldMap.


        :param transaction_currency: The transaction_currency of this TransactionFieldMap.  # noqa: E501
        :type transaction_currency: str
        """
        if self.local_vars_configuration.client_side_validation and transaction_currency is None:  # noqa: E501
            raise ValueError("Invalid value for `transaction_currency`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                transaction_currency is not None and len(transaction_currency) > 1024):
            raise ValueError("Invalid value for `transaction_currency`, length must be less than or equal to `1024`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                transaction_currency is not None and len(transaction_currency) < 0):
            raise ValueError("Invalid value for `transaction_currency`, length must be greater than or equal to `0`")  # noqa: E501

        self._transaction_currency = transaction_currency

    @property
    def exchange_rate(self):
        """Gets the exchange_rate of this TransactionFieldMap.  # noqa: E501


        :return: The exchange_rate of this TransactionFieldMap.  # noqa: E501
        :rtype: str
        """
        return self._exchange_rate

    @exchange_rate.setter
    def exchange_rate(self, exchange_rate):
        """Sets the exchange_rate of this TransactionFieldMap.


        :param exchange_rate: The exchange_rate of this TransactionFieldMap.  # noqa: E501
        :type exchange_rate: str
        """
        if (self.local_vars_configuration.client_side_validation and
                exchange_rate is not None and len(exchange_rate) > 1024):
            raise ValueError("Invalid value for `exchange_rate`, length must be less than or equal to `1024`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                exchange_rate is not None and len(exchange_rate) < 0):
            raise ValueError("Invalid value for `exchange_rate`, length must be greater than or equal to `0`")  # noqa: E501

        self._exchange_rate = exchange_rate

    @property
    def total_consideration(self):
        """Gets the total_consideration of this TransactionFieldMap.  # noqa: E501


        :return: The total_consideration of this TransactionFieldMap.  # noqa: E501
        :rtype: lusid.TransactionCurrencyAndAmount
        """
        return self._total_consideration

    @total_consideration.setter
    def total_consideration(self, total_consideration):
        """Sets the total_consideration of this TransactionFieldMap.


        :param total_consideration: The total_consideration of this TransactionFieldMap.  # noqa: E501
        :type total_consideration: lusid.TransactionCurrencyAndAmount
        """
        if self.local_vars_configuration.client_side_validation and total_consideration is None:  # noqa: E501
            raise ValueError("Invalid value for `total_consideration`, must not be `None`")  # noqa: E501

        self._total_consideration = total_consideration

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
        if not isinstance(other, TransactionFieldMap):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TransactionFieldMap):
            return True

        return self.to_dict() != other.to_dict()
