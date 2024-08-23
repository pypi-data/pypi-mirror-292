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


class JournalEntryLinesQueryParameters(object):
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
        'start': 'DateOrDiaryEntry',
        'end': 'DateOrDiaryEntry',
        'date_mode': 'str',
        'general_ledger_profile_code': 'str',
        'property_keys': 'list[str]'
    }

    attribute_map = {
        'start': 'start',
        'end': 'end',
        'date_mode': 'dateMode',
        'general_ledger_profile_code': 'generalLedgerProfileCode',
        'property_keys': 'propertyKeys'
    }

    required_map = {
        'start': 'optional',
        'end': 'optional',
        'date_mode': 'optional',
        'general_ledger_profile_code': 'optional',
        'property_keys': 'optional'
    }

    def __init__(self, start=None, end=None, date_mode=None, general_ledger_profile_code=None, property_keys=None, local_vars_configuration=None):  # noqa: E501
        """JournalEntryLinesQueryParameters - a model defined in OpenAPI"
        
        :param start: 
        :type start: lusid.DateOrDiaryEntry
        :param end: 
        :type end: lusid.DateOrDiaryEntry
        :param date_mode:  The mode of calculation of the journal entry lines. The available values are: ActivityDate, AccountingDate.
        :type date_mode: str
        :param general_ledger_profile_code:  The optional code of a general ledger profile used to decorate journal entry lines with levels.
        :type general_ledger_profile_code: str
        :param property_keys:  A list of property keys from the 'Instrument', 'Transaction', 'Portfolio', 'Account', 'LegalEntity' or 'CustodianAccount' domain to decorate onto the journal entry lines.
        :type property_keys: list[str]

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._start = None
        self._end = None
        self._date_mode = None
        self._general_ledger_profile_code = None
        self._property_keys = None
        self.discriminator = None

        if start is not None:
            self.start = start
        if end is not None:
            self.end = end
        self.date_mode = date_mode
        self.general_ledger_profile_code = general_ledger_profile_code
        self.property_keys = property_keys

    @property
    def start(self):
        """Gets the start of this JournalEntryLinesQueryParameters.  # noqa: E501


        :return: The start of this JournalEntryLinesQueryParameters.  # noqa: E501
        :rtype: lusid.DateOrDiaryEntry
        """
        return self._start

    @start.setter
    def start(self, start):
        """Sets the start of this JournalEntryLinesQueryParameters.


        :param start: The start of this JournalEntryLinesQueryParameters.  # noqa: E501
        :type start: lusid.DateOrDiaryEntry
        """

        self._start = start

    @property
    def end(self):
        """Gets the end of this JournalEntryLinesQueryParameters.  # noqa: E501


        :return: The end of this JournalEntryLinesQueryParameters.  # noqa: E501
        :rtype: lusid.DateOrDiaryEntry
        """
        return self._end

    @end.setter
    def end(self, end):
        """Sets the end of this JournalEntryLinesQueryParameters.


        :param end: The end of this JournalEntryLinesQueryParameters.  # noqa: E501
        :type end: lusid.DateOrDiaryEntry
        """

        self._end = end

    @property
    def date_mode(self):
        """Gets the date_mode of this JournalEntryLinesQueryParameters.  # noqa: E501

        The mode of calculation of the journal entry lines. The available values are: ActivityDate, AccountingDate.  # noqa: E501

        :return: The date_mode of this JournalEntryLinesQueryParameters.  # noqa: E501
        :rtype: str
        """
        return self._date_mode

    @date_mode.setter
    def date_mode(self, date_mode):
        """Sets the date_mode of this JournalEntryLinesQueryParameters.

        The mode of calculation of the journal entry lines. The available values are: ActivityDate, AccountingDate.  # noqa: E501

        :param date_mode: The date_mode of this JournalEntryLinesQueryParameters.  # noqa: E501
        :type date_mode: str
        """

        self._date_mode = date_mode

    @property
    def general_ledger_profile_code(self):
        """Gets the general_ledger_profile_code of this JournalEntryLinesQueryParameters.  # noqa: E501

        The optional code of a general ledger profile used to decorate journal entry lines with levels.  # noqa: E501

        :return: The general_ledger_profile_code of this JournalEntryLinesQueryParameters.  # noqa: E501
        :rtype: str
        """
        return self._general_ledger_profile_code

    @general_ledger_profile_code.setter
    def general_ledger_profile_code(self, general_ledger_profile_code):
        """Sets the general_ledger_profile_code of this JournalEntryLinesQueryParameters.

        The optional code of a general ledger profile used to decorate journal entry lines with levels.  # noqa: E501

        :param general_ledger_profile_code: The general_ledger_profile_code of this JournalEntryLinesQueryParameters.  # noqa: E501
        :type general_ledger_profile_code: str
        """
        if (self.local_vars_configuration.client_side_validation and
                general_ledger_profile_code is not None and len(general_ledger_profile_code) > 64):
            raise ValueError("Invalid value for `general_ledger_profile_code`, length must be less than or equal to `64`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                general_ledger_profile_code is not None and len(general_ledger_profile_code) < 1):
            raise ValueError("Invalid value for `general_ledger_profile_code`, length must be greater than or equal to `1`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                general_ledger_profile_code is not None and not re.search(r'^[a-zA-Z0-9\-_]+$', general_ledger_profile_code)):  # noqa: E501
            raise ValueError(r"Invalid value for `general_ledger_profile_code`, must be a follow pattern or equal to `/^[a-zA-Z0-9\-_]+$/`")  # noqa: E501

        self._general_ledger_profile_code = general_ledger_profile_code

    @property
    def property_keys(self):
        """Gets the property_keys of this JournalEntryLinesQueryParameters.  # noqa: E501

        A list of property keys from the 'Instrument', 'Transaction', 'Portfolio', 'Account', 'LegalEntity' or 'CustodianAccount' domain to decorate onto the journal entry lines.  # noqa: E501

        :return: The property_keys of this JournalEntryLinesQueryParameters.  # noqa: E501
        :rtype: list[str]
        """
        return self._property_keys

    @property_keys.setter
    def property_keys(self, property_keys):
        """Sets the property_keys of this JournalEntryLinesQueryParameters.

        A list of property keys from the 'Instrument', 'Transaction', 'Portfolio', 'Account', 'LegalEntity' or 'CustodianAccount' domain to decorate onto the journal entry lines.  # noqa: E501

        :param property_keys: The property_keys of this JournalEntryLinesQueryParameters.  # noqa: E501
        :type property_keys: list[str]
        """

        self._property_keys = property_keys

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
        if not isinstance(other, JournalEntryLinesQueryParameters):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, JournalEntryLinesQueryParameters):
            return True

        return self.to_dict() != other.to_dict()
