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


class LineageMember(object):
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
        'index': 'int',
        'label': 'str',
        'sub_label': 'str',
        'info_type': 'str',
        'information': 'str'
    }

    attribute_map = {
        'index': 'index',
        'label': 'label',
        'sub_label': 'subLabel',
        'info_type': 'infoType',
        'information': 'information'
    }

    required_map = {
        'index': 'required',
        'label': 'required',
        'sub_label': 'required',
        'info_type': 'optional',
        'information': 'optional'
    }

    def __init__(self, index=None, label=None, sub_label=None, info_type=None, information=None, local_vars_configuration=None):  # noqa: E501
        """LineageMember - a model defined in OpenAPI"
        
        :param index:  Index to demonstrate position of lineage member in overall lineage (required)
        :type index: int
        :param label:  Label of the step corresponding to this lineage member (required)
        :type label: str
        :param sub_label:  SubLabel of the step corresponding to this lineage member (required)
        :type sub_label: str
        :param info_type:  Optional. Type of Information
        :type info_type: str
        :param information:  Optional. Information for the step corresponding to this lineage member, of type InfoType
        :type information: str

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._index = None
        self._label = None
        self._sub_label = None
        self._info_type = None
        self._information = None
        self.discriminator = None

        self.index = index
        self.label = label
        self.sub_label = sub_label
        self.info_type = info_type
        self.information = information

    @property
    def index(self):
        """Gets the index of this LineageMember.  # noqa: E501

        Index to demonstrate position of lineage member in overall lineage  # noqa: E501

        :return: The index of this LineageMember.  # noqa: E501
        :rtype: int
        """
        return self._index

    @index.setter
    def index(self, index):
        """Sets the index of this LineageMember.

        Index to demonstrate position of lineage member in overall lineage  # noqa: E501

        :param index: The index of this LineageMember.  # noqa: E501
        :type index: int
        """
        if self.local_vars_configuration.client_side_validation and index is None:  # noqa: E501
            raise ValueError("Invalid value for `index`, must not be `None`")  # noqa: E501

        self._index = index

    @property
    def label(self):
        """Gets the label of this LineageMember.  # noqa: E501

        Label of the step corresponding to this lineage member  # noqa: E501

        :return: The label of this LineageMember.  # noqa: E501
        :rtype: str
        """
        return self._label

    @label.setter
    def label(self, label):
        """Sets the label of this LineageMember.

        Label of the step corresponding to this lineage member  # noqa: E501

        :param label: The label of this LineageMember.  # noqa: E501
        :type label: str
        """
        if self.local_vars_configuration.client_side_validation and label is None:  # noqa: E501
            raise ValueError("Invalid value for `label`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                label is not None and len(label) > 6000):
            raise ValueError("Invalid value for `label`, length must be less than or equal to `6000`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                label is not None and len(label) < 0):
            raise ValueError("Invalid value for `label`, length must be greater than or equal to `0`")  # noqa: E501

        self._label = label

    @property
    def sub_label(self):
        """Gets the sub_label of this LineageMember.  # noqa: E501

        SubLabel of the step corresponding to this lineage member  # noqa: E501

        :return: The sub_label of this LineageMember.  # noqa: E501
        :rtype: str
        """
        return self._sub_label

    @sub_label.setter
    def sub_label(self, sub_label):
        """Sets the sub_label of this LineageMember.

        SubLabel of the step corresponding to this lineage member  # noqa: E501

        :param sub_label: The sub_label of this LineageMember.  # noqa: E501
        :type sub_label: str
        """
        if self.local_vars_configuration.client_side_validation and sub_label is None:  # noqa: E501
            raise ValueError("Invalid value for `sub_label`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                sub_label is not None and len(sub_label) > 6000):
            raise ValueError("Invalid value for `sub_label`, length must be less than or equal to `6000`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                sub_label is not None and len(sub_label) < 0):
            raise ValueError("Invalid value for `sub_label`, length must be greater than or equal to `0`")  # noqa: E501

        self._sub_label = sub_label

    @property
    def info_type(self):
        """Gets the info_type of this LineageMember.  # noqa: E501

        Optional. Type of Information  # noqa: E501

        :return: The info_type of this LineageMember.  # noqa: E501
        :rtype: str
        """
        return self._info_type

    @info_type.setter
    def info_type(self, info_type):
        """Sets the info_type of this LineageMember.

        Optional. Type of Information  # noqa: E501

        :param info_type: The info_type of this LineageMember.  # noqa: E501
        :type info_type: str
        """
        if (self.local_vars_configuration.client_side_validation and
                info_type is not None and len(info_type) > 6000):
            raise ValueError("Invalid value for `info_type`, length must be less than or equal to `6000`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                info_type is not None and len(info_type) < 0):
            raise ValueError("Invalid value for `info_type`, length must be greater than or equal to `0`")  # noqa: E501

        self._info_type = info_type

    @property
    def information(self):
        """Gets the information of this LineageMember.  # noqa: E501

        Optional. Information for the step corresponding to this lineage member, of type InfoType  # noqa: E501

        :return: The information of this LineageMember.  # noqa: E501
        :rtype: str
        """
        return self._information

    @information.setter
    def information(self, information):
        """Sets the information of this LineageMember.

        Optional. Information for the step corresponding to this lineage member, of type InfoType  # noqa: E501

        :param information: The information of this LineageMember.  # noqa: E501
        :type information: str
        """
        if (self.local_vars_configuration.client_side_validation and
                information is not None and len(information) > 6000):
            raise ValueError("Invalid value for `information`, length must be less than or equal to `6000`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                information is not None and len(information) < 0):
            raise ValueError("Invalid value for `information`, length must be greater than or equal to `0`")  # noqa: E501

        self._information = information

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
        if not isinstance(other, LineageMember):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, LineageMember):
            return True

        return self.to_dict() != other.to_dict()
