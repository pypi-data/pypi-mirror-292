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


class TemplateField(object):
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
        'field_name': 'str',
        'specificity': 'str',
        'description': 'str',
        'type': 'str',
        'availability': 'str',
        'usage': 'list[str]'
    }

    attribute_map = {
        'field_name': 'fieldName',
        'specificity': 'specificity',
        'description': 'description',
        'type': 'type',
        'availability': 'availability',
        'usage': 'usage'
    }

    required_map = {
        'field_name': 'required',
        'specificity': 'required',
        'description': 'required',
        'type': 'required',
        'availability': 'required',
        'usage': 'required'
    }

    def __init__(self, field_name=None, specificity=None, description=None, type=None, availability=None, usage=None, local_vars_configuration=None):  # noqa: E501
        """TemplateField - a model defined in OpenAPI"
        
        :param field_name:  (required)
        :type field_name: str
        :param specificity:  (required)
        :type specificity: str
        :param description:  (required)
        :type description: str
        :param type:  (required)
        :type type: str
        :param availability:  (required)
        :type availability: str
        :param usage:  (required)
        :type usage: list[str]

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._field_name = None
        self._specificity = None
        self._description = None
        self._type = None
        self._availability = None
        self._usage = None
        self.discriminator = None

        self.field_name = field_name
        self.specificity = specificity
        self.description = description
        self.type = type
        self.availability = availability
        self.usage = usage

    @property
    def field_name(self):
        """Gets the field_name of this TemplateField.  # noqa: E501


        :return: The field_name of this TemplateField.  # noqa: E501
        :rtype: str
        """
        return self._field_name

    @field_name.setter
    def field_name(self, field_name):
        """Sets the field_name of this TemplateField.


        :param field_name: The field_name of this TemplateField.  # noqa: E501
        :type field_name: str
        """
        if self.local_vars_configuration.client_side_validation and field_name is None:  # noqa: E501
            raise ValueError("Invalid value for `field_name`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                field_name is not None and len(field_name) < 1):
            raise ValueError("Invalid value for `field_name`, length must be greater than or equal to `1`")  # noqa: E501

        self._field_name = field_name

    @property
    def specificity(self):
        """Gets the specificity of this TemplateField.  # noqa: E501


        :return: The specificity of this TemplateField.  # noqa: E501
        :rtype: str
        """
        return self._specificity

    @specificity.setter
    def specificity(self, specificity):
        """Sets the specificity of this TemplateField.


        :param specificity: The specificity of this TemplateField.  # noqa: E501
        :type specificity: str
        """
        if self.local_vars_configuration.client_side_validation and specificity is None:  # noqa: E501
            raise ValueError("Invalid value for `specificity`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                specificity is not None and len(specificity) < 1):
            raise ValueError("Invalid value for `specificity`, length must be greater than or equal to `1`")  # noqa: E501

        self._specificity = specificity

    @property
    def description(self):
        """Gets the description of this TemplateField.  # noqa: E501


        :return: The description of this TemplateField.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this TemplateField.


        :param description: The description of this TemplateField.  # noqa: E501
        :type description: str
        """
        if self.local_vars_configuration.client_side_validation and description is None:  # noqa: E501
            raise ValueError("Invalid value for `description`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                description is not None and len(description) < 1):
            raise ValueError("Invalid value for `description`, length must be greater than or equal to `1`")  # noqa: E501

        self._description = description

    @property
    def type(self):
        """Gets the type of this TemplateField.  # noqa: E501


        :return: The type of this TemplateField.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this TemplateField.


        :param type: The type of this TemplateField.  # noqa: E501
        :type type: str
        """
        if self.local_vars_configuration.client_side_validation and type is None:  # noqa: E501
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                type is not None and len(type) < 1):
            raise ValueError("Invalid value for `type`, length must be greater than or equal to `1`")  # noqa: E501

        self._type = type

    @property
    def availability(self):
        """Gets the availability of this TemplateField.  # noqa: E501


        :return: The availability of this TemplateField.  # noqa: E501
        :rtype: str
        """
        return self._availability

    @availability.setter
    def availability(self, availability):
        """Sets the availability of this TemplateField.


        :param availability: The availability of this TemplateField.  # noqa: E501
        :type availability: str
        """
        if self.local_vars_configuration.client_side_validation and availability is None:  # noqa: E501
            raise ValueError("Invalid value for `availability`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                availability is not None and len(availability) < 1):
            raise ValueError("Invalid value for `availability`, length must be greater than or equal to `1`")  # noqa: E501

        self._availability = availability

    @property
    def usage(self):
        """Gets the usage of this TemplateField.  # noqa: E501


        :return: The usage of this TemplateField.  # noqa: E501
        :rtype: list[str]
        """
        return self._usage

    @usage.setter
    def usage(self, usage):
        """Sets the usage of this TemplateField.


        :param usage: The usage of this TemplateField.  # noqa: E501
        :type usage: list[str]
        """
        if self.local_vars_configuration.client_side_validation and usage is None:  # noqa: E501
            raise ValueError("Invalid value for `usage`, must not be `None`")  # noqa: E501

        self._usage = usage

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
        if not isinstance(other, TemplateField):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TemplateField):
            return True

        return self.to_dict() != other.to_dict()
