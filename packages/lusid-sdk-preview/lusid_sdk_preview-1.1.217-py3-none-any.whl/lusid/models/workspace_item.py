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


class WorkspaceItem(object):
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
        'type': 'str',
        'format': 'int',
        'name': 'str',
        'description': 'str',
        'content': 'str',
        'version': 'Version',
        'links': 'list[Link]'
    }

    attribute_map = {
        'type': 'type',
        'format': 'format',
        'name': 'name',
        'description': 'description',
        'content': 'content',
        'version': 'version',
        'links': 'links'
    }

    required_map = {
        'type': 'required',
        'format': 'required',
        'name': 'required',
        'description': 'required',
        'content': 'required',
        'version': 'optional',
        'links': 'optional'
    }

    def __init__(self, type=None, format=None, name=None, description=None, content=None, version=None, links=None, local_vars_configuration=None):  # noqa: E501
        """WorkspaceItem - a model defined in OpenAPI"
        
        :param type:  The type of the workspace item. (required)
        :type type: str
        :param format:  A simple integer format identifier. (required)
        :type format: int
        :param name:  A workspace item's name; a unique identifier. (required)
        :type name: str
        :param description:  The description of a workspace item. (required)
        :type description: str
        :param content:  The content associated with a workspace item. (required)
        :type content: str
        :param version: 
        :type version: lusid.Version
        :param links:  Collection of links.
        :type links: list[lusid.Link]

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._type = None
        self._format = None
        self._name = None
        self._description = None
        self._content = None
        self._version = None
        self._links = None
        self.discriminator = None

        self.type = type
        self.format = format
        self.name = name
        self.description = description
        self.content = content
        if version is not None:
            self.version = version
        self.links = links

    @property
    def type(self):
        """Gets the type of this WorkspaceItem.  # noqa: E501

        The type of the workspace item.  # noqa: E501

        :return: The type of this WorkspaceItem.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this WorkspaceItem.

        The type of the workspace item.  # noqa: E501

        :param type: The type of this WorkspaceItem.  # noqa: E501
        :type type: str
        """
        if self.local_vars_configuration.client_side_validation and type is None:  # noqa: E501
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                type is not None and len(type) < 1):
            raise ValueError("Invalid value for `type`, length must be greater than or equal to `1`")  # noqa: E501

        self._type = type

    @property
    def format(self):
        """Gets the format of this WorkspaceItem.  # noqa: E501

        A simple integer format identifier.  # noqa: E501

        :return: The format of this WorkspaceItem.  # noqa: E501
        :rtype: int
        """
        return self._format

    @format.setter
    def format(self, format):
        """Sets the format of this WorkspaceItem.

        A simple integer format identifier.  # noqa: E501

        :param format: The format of this WorkspaceItem.  # noqa: E501
        :type format: int
        """
        if self.local_vars_configuration.client_side_validation and format is None:  # noqa: E501
            raise ValueError("Invalid value for `format`, must not be `None`")  # noqa: E501

        self._format = format

    @property
    def name(self):
        """Gets the name of this WorkspaceItem.  # noqa: E501

        A workspace item's name; a unique identifier.  # noqa: E501

        :return: The name of this WorkspaceItem.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this WorkspaceItem.

        A workspace item's name; a unique identifier.  # noqa: E501

        :param name: The name of this WorkspaceItem.  # noqa: E501
        :type name: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                name is not None and len(name) < 1):
            raise ValueError("Invalid value for `name`, length must be greater than or equal to `1`")  # noqa: E501

        self._name = name

    @property
    def description(self):
        """Gets the description of this WorkspaceItem.  # noqa: E501

        The description of a workspace item.  # noqa: E501

        :return: The description of this WorkspaceItem.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this WorkspaceItem.

        The description of a workspace item.  # noqa: E501

        :param description: The description of this WorkspaceItem.  # noqa: E501
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
    def content(self):
        """Gets the content of this WorkspaceItem.  # noqa: E501

        The content associated with a workspace item.  # noqa: E501

        :return: The content of this WorkspaceItem.  # noqa: E501
        :rtype: str
        """
        return self._content

    @content.setter
    def content(self, content):
        """Sets the content of this WorkspaceItem.

        The content associated with a workspace item.  # noqa: E501

        :param content: The content of this WorkspaceItem.  # noqa: E501
        :type content: str
        """
        if self.local_vars_configuration.client_side_validation and content is None:  # noqa: E501
            raise ValueError("Invalid value for `content`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                content is not None and len(content) > 6000):
            raise ValueError("Invalid value for `content`, length must be less than or equal to `6000`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                content is not None and len(content) < 0):
            raise ValueError("Invalid value for `content`, length must be greater than or equal to `0`")  # noqa: E501

        self._content = content

    @property
    def version(self):
        """Gets the version of this WorkspaceItem.  # noqa: E501


        :return: The version of this WorkspaceItem.  # noqa: E501
        :rtype: lusid.Version
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this WorkspaceItem.


        :param version: The version of this WorkspaceItem.  # noqa: E501
        :type version: lusid.Version
        """

        self._version = version

    @property
    def links(self):
        """Gets the links of this WorkspaceItem.  # noqa: E501

        Collection of links.  # noqa: E501

        :return: The links of this WorkspaceItem.  # noqa: E501
        :rtype: list[lusid.Link]
        """
        return self._links

    @links.setter
    def links(self, links):
        """Sets the links of this WorkspaceItem.

        Collection of links.  # noqa: E501

        :param links: The links of this WorkspaceItem.  # noqa: E501
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
        if not isinstance(other, WorkspaceItem):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, WorkspaceItem):
            return True

        return self.to_dict() != other.to_dict()
