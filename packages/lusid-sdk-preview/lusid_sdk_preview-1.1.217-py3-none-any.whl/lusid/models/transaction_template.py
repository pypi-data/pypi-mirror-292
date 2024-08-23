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


class TransactionTemplate(object):
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
        'instrument_type': 'str',
        'instrument_event_type': 'str',
        'description': 'str',
        'scope': 'str',
        'component_transactions': 'list[ComponentTransaction]',
        'links': 'list[Link]'
    }

    attribute_map = {
        'instrument_type': 'instrumentType',
        'instrument_event_type': 'instrumentEventType',
        'description': 'description',
        'scope': 'scope',
        'component_transactions': 'componentTransactions',
        'links': 'links'
    }

    required_map = {
        'instrument_type': 'required',
        'instrument_event_type': 'required',
        'description': 'required',
        'scope': 'required',
        'component_transactions': 'required',
        'links': 'optional'
    }

    def __init__(self, instrument_type=None, instrument_event_type=None, description=None, scope=None, component_transactions=None, links=None, local_vars_configuration=None):  # noqa: E501
        """TransactionTemplate - a model defined in OpenAPI"
        
        :param instrument_type:  A value that represents the instrument type. (required)
        :type instrument_type: str
        :param instrument_event_type:  A value that represents the instrument event type. (required)
        :type instrument_event_type: str
        :param description:  The description of the transaction template. (required)
        :type description: str
        :param scope:  The scope in which the transaction template resides. (required)
        :type scope: str
        :param component_transactions:  A set of component transactions that relate to the template to be created. (required)
        :type component_transactions: list[lusid.ComponentTransaction]
        :param links:  Collection of links.
        :type links: list[lusid.Link]

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._instrument_type = None
        self._instrument_event_type = None
        self._description = None
        self._scope = None
        self._component_transactions = None
        self._links = None
        self.discriminator = None

        self.instrument_type = instrument_type
        self.instrument_event_type = instrument_event_type
        self.description = description
        self.scope = scope
        self.component_transactions = component_transactions
        self.links = links

    @property
    def instrument_type(self):
        """Gets the instrument_type of this TransactionTemplate.  # noqa: E501

        A value that represents the instrument type.  # noqa: E501

        :return: The instrument_type of this TransactionTemplate.  # noqa: E501
        :rtype: str
        """
        return self._instrument_type

    @instrument_type.setter
    def instrument_type(self, instrument_type):
        """Sets the instrument_type of this TransactionTemplate.

        A value that represents the instrument type.  # noqa: E501

        :param instrument_type: The instrument_type of this TransactionTemplate.  # noqa: E501
        :type instrument_type: str
        """
        if self.local_vars_configuration.client_side_validation and instrument_type is None:  # noqa: E501
            raise ValueError("Invalid value for `instrument_type`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                instrument_type is not None and len(instrument_type) < 1):
            raise ValueError("Invalid value for `instrument_type`, length must be greater than or equal to `1`")  # noqa: E501

        self._instrument_type = instrument_type

    @property
    def instrument_event_type(self):
        """Gets the instrument_event_type of this TransactionTemplate.  # noqa: E501

        A value that represents the instrument event type.  # noqa: E501

        :return: The instrument_event_type of this TransactionTemplate.  # noqa: E501
        :rtype: str
        """
        return self._instrument_event_type

    @instrument_event_type.setter
    def instrument_event_type(self, instrument_event_type):
        """Sets the instrument_event_type of this TransactionTemplate.

        A value that represents the instrument event type.  # noqa: E501

        :param instrument_event_type: The instrument_event_type of this TransactionTemplate.  # noqa: E501
        :type instrument_event_type: str
        """
        if self.local_vars_configuration.client_side_validation and instrument_event_type is None:  # noqa: E501
            raise ValueError("Invalid value for `instrument_event_type`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                instrument_event_type is not None and len(instrument_event_type) < 1):
            raise ValueError("Invalid value for `instrument_event_type`, length must be greater than or equal to `1`")  # noqa: E501

        self._instrument_event_type = instrument_event_type

    @property
    def description(self):
        """Gets the description of this TransactionTemplate.  # noqa: E501

        The description of the transaction template.  # noqa: E501

        :return: The description of this TransactionTemplate.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this TransactionTemplate.

        The description of the transaction template.  # noqa: E501

        :param description: The description of this TransactionTemplate.  # noqa: E501
        :type description: str
        """
        if self.local_vars_configuration.client_side_validation and description is None:  # noqa: E501
            raise ValueError("Invalid value for `description`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                description is not None and len(description) < 1):
            raise ValueError("Invalid value for `description`, length must be greater than or equal to `1`")  # noqa: E501

        self._description = description

    @property
    def scope(self):
        """Gets the scope of this TransactionTemplate.  # noqa: E501

        The scope in which the transaction template resides.  # noqa: E501

        :return: The scope of this TransactionTemplate.  # noqa: E501
        :rtype: str
        """
        return self._scope

    @scope.setter
    def scope(self, scope):
        """Sets the scope of this TransactionTemplate.

        The scope in which the transaction template resides.  # noqa: E501

        :param scope: The scope of this TransactionTemplate.  # noqa: E501
        :type scope: str
        """
        if self.local_vars_configuration.client_side_validation and scope is None:  # noqa: E501
            raise ValueError("Invalid value for `scope`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                scope is not None and len(scope) < 1):
            raise ValueError("Invalid value for `scope`, length must be greater than or equal to `1`")  # noqa: E501

        self._scope = scope

    @property
    def component_transactions(self):
        """Gets the component_transactions of this TransactionTemplate.  # noqa: E501

        A set of component transactions that relate to the template to be created.  # noqa: E501

        :return: The component_transactions of this TransactionTemplate.  # noqa: E501
        :rtype: list[lusid.ComponentTransaction]
        """
        return self._component_transactions

    @component_transactions.setter
    def component_transactions(self, component_transactions):
        """Sets the component_transactions of this TransactionTemplate.

        A set of component transactions that relate to the template to be created.  # noqa: E501

        :param component_transactions: The component_transactions of this TransactionTemplate.  # noqa: E501
        :type component_transactions: list[lusid.ComponentTransaction]
        """
        if self.local_vars_configuration.client_side_validation and component_transactions is None:  # noqa: E501
            raise ValueError("Invalid value for `component_transactions`, must not be `None`")  # noqa: E501

        self._component_transactions = component_transactions

    @property
    def links(self):
        """Gets the links of this TransactionTemplate.  # noqa: E501

        Collection of links.  # noqa: E501

        :return: The links of this TransactionTemplate.  # noqa: E501
        :rtype: list[lusid.Link]
        """
        return self._links

    @links.setter
    def links(self, links):
        """Sets the links of this TransactionTemplate.

        Collection of links.  # noqa: E501

        :param links: The links of this TransactionTemplate.  # noqa: E501
        :type links: list[lusid.Link]
        """

        self._links = links

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
        if not isinstance(other, TransactionTemplate):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TransactionTemplate):
            return True

        return self.to_dict() != other.to_dict()
