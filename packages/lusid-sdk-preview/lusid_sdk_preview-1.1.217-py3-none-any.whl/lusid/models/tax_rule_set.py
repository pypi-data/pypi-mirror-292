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


class TaxRuleSet(object):
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
        'id': 'ResourceId',
        'display_name': 'str',
        'description': 'str',
        'output_property_key': 'str',
        'rules': 'list[TaxRule]',
        'version': 'Version',
        'links': 'list[Link]'
    }

    attribute_map = {
        'id': 'id',
        'display_name': 'displayName',
        'description': 'description',
        'output_property_key': 'outputPropertyKey',
        'rules': 'rules',
        'version': 'version',
        'links': 'links'
    }

    required_map = {
        'id': 'required',
        'display_name': 'required',
        'description': 'required',
        'output_property_key': 'required',
        'rules': 'required',
        'version': 'optional',
        'links': 'optional'
    }

    def __init__(self, id=None, display_name=None, description=None, output_property_key=None, rules=None, version=None, links=None, local_vars_configuration=None):  # noqa: E501
        """TaxRuleSet - a model defined in OpenAPI"
        
        :param id:  (required)
        :type id: lusid.ResourceId
        :param display_name:  A user-friendly name (required)
        :type display_name: str
        :param description:  A description of what this rule set is for (required)
        :type description: str
        :param output_property_key:  The property key that this rule set will write to (required)
        :type output_property_key: str
        :param rules:  The rules of this rule set, which stipulate what rate to apply (i.e. write to the OutputPropertyKey) under certain conditions (required)
        :type rules: list[lusid.TaxRule]
        :param version: 
        :type version: lusid.Version
        :param links:  Collection of links.
        :type links: list[lusid.Link]

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._display_name = None
        self._description = None
        self._output_property_key = None
        self._rules = None
        self._version = None
        self._links = None
        self.discriminator = None

        self.id = id
        self.display_name = display_name
        self.description = description
        self.output_property_key = output_property_key
        self.rules = rules
        if version is not None:
            self.version = version
        self.links = links

    @property
    def id(self):
        """Gets the id of this TaxRuleSet.  # noqa: E501


        :return: The id of this TaxRuleSet.  # noqa: E501
        :rtype: lusid.ResourceId
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this TaxRuleSet.


        :param id: The id of this TaxRuleSet.  # noqa: E501
        :type id: lusid.ResourceId
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def display_name(self):
        """Gets the display_name of this TaxRuleSet.  # noqa: E501

        A user-friendly name  # noqa: E501

        :return: The display_name of this TaxRuleSet.  # noqa: E501
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """Sets the display_name of this TaxRuleSet.

        A user-friendly name  # noqa: E501

        :param display_name: The display_name of this TaxRuleSet.  # noqa: E501
        :type display_name: str
        """
        if self.local_vars_configuration.client_side_validation and display_name is None:  # noqa: E501
            raise ValueError("Invalid value for `display_name`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                display_name is not None and len(display_name) > 1024):
            raise ValueError("Invalid value for `display_name`, length must be less than or equal to `1024`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                display_name is not None and len(display_name) < 0):
            raise ValueError("Invalid value for `display_name`, length must be greater than or equal to `0`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                display_name is not None and not re.search(r'^[\s\S]*$', display_name)):  # noqa: E501
            raise ValueError(r"Invalid value for `display_name`, must be a follow pattern or equal to `/^[\s\S]*$/`")  # noqa: E501

        self._display_name = display_name

    @property
    def description(self):
        """Gets the description of this TaxRuleSet.  # noqa: E501

        A description of what this rule set is for  # noqa: E501

        :return: The description of this TaxRuleSet.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this TaxRuleSet.

        A description of what this rule set is for  # noqa: E501

        :param description: The description of this TaxRuleSet.  # noqa: E501
        :type description: str
        """
        if self.local_vars_configuration.client_side_validation and description is None:  # noqa: E501
            raise ValueError("Invalid value for `description`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                description is not None and len(description) > 1024):
            raise ValueError("Invalid value for `description`, length must be less than or equal to `1024`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                description is not None and len(description) < 0):
            raise ValueError("Invalid value for `description`, length must be greater than or equal to `0`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                description is not None and not re.search(r'^[\s\S]*$', description)):  # noqa: E501
            raise ValueError(r"Invalid value for `description`, must be a follow pattern or equal to `/^[\s\S]*$/`")  # noqa: E501

        self._description = description

    @property
    def output_property_key(self):
        """Gets the output_property_key of this TaxRuleSet.  # noqa: E501

        The property key that this rule set will write to  # noqa: E501

        :return: The output_property_key of this TaxRuleSet.  # noqa: E501
        :rtype: str
        """
        return self._output_property_key

    @output_property_key.setter
    def output_property_key(self, output_property_key):
        """Sets the output_property_key of this TaxRuleSet.

        The property key that this rule set will write to  # noqa: E501

        :param output_property_key: The output_property_key of this TaxRuleSet.  # noqa: E501
        :type output_property_key: str
        """
        if self.local_vars_configuration.client_side_validation and output_property_key is None:  # noqa: E501
            raise ValueError("Invalid value for `output_property_key`, must not be `None`")  # noqa: E501

        self._output_property_key = output_property_key

    @property
    def rules(self):
        """Gets the rules of this TaxRuleSet.  # noqa: E501

        The rules of this rule set, which stipulate what rate to apply (i.e. write to the OutputPropertyKey) under certain conditions  # noqa: E501

        :return: The rules of this TaxRuleSet.  # noqa: E501
        :rtype: list[lusid.TaxRule]
        """
        return self._rules

    @rules.setter
    def rules(self, rules):
        """Sets the rules of this TaxRuleSet.

        The rules of this rule set, which stipulate what rate to apply (i.e. write to the OutputPropertyKey) under certain conditions  # noqa: E501

        :param rules: The rules of this TaxRuleSet.  # noqa: E501
        :type rules: list[lusid.TaxRule]
        """
        if self.local_vars_configuration.client_side_validation and rules is None:  # noqa: E501
            raise ValueError("Invalid value for `rules`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                rules is not None and len(rules) > 100):
            raise ValueError("Invalid value for `rules`, number of items must be less than or equal to `100`")  # noqa: E501

        self._rules = rules

    @property
    def version(self):
        """Gets the version of this TaxRuleSet.  # noqa: E501


        :return: The version of this TaxRuleSet.  # noqa: E501
        :rtype: lusid.Version
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this TaxRuleSet.


        :param version: The version of this TaxRuleSet.  # noqa: E501
        :type version: lusid.Version
        """

        self._version = version

    @property
    def links(self):
        """Gets the links of this TaxRuleSet.  # noqa: E501

        Collection of links.  # noqa: E501

        :return: The links of this TaxRuleSet.  # noqa: E501
        :rtype: list[lusid.Link]
        """
        return self._links

    @links.setter
    def links(self, links):
        """Sets the links of this TaxRuleSet.

        Collection of links.  # noqa: E501

        :param links: The links of this TaxRuleSet.  # noqa: E501
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
        if not isinstance(other, TaxRuleSet):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TaxRuleSet):
            return True

        return self.to_dict() != other.to_dict()
