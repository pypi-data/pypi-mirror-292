# coding: utf-8

"""
    vke

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class SystemVolumeForCreateNodePoolInput(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'size': 'int',
        'type': 'str'
    }

    attribute_map = {
        'size': 'Size',
        'type': 'Type'
    }

    def __init__(self, size=None, type=None, _configuration=None):  # noqa: E501
        """SystemVolumeForCreateNodePoolInput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._size = None
        self._type = None
        self.discriminator = None

        if size is not None:
            self.size = size
        if type is not None:
            self.type = type

    @property
    def size(self):
        """Gets the size of this SystemVolumeForCreateNodePoolInput.  # noqa: E501


        :return: The size of this SystemVolumeForCreateNodePoolInput.  # noqa: E501
        :rtype: int
        """
        return self._size

    @size.setter
    def size(self, size):
        """Sets the size of this SystemVolumeForCreateNodePoolInput.


        :param size: The size of this SystemVolumeForCreateNodePoolInput.  # noqa: E501
        :type: int
        """

        self._size = size

    @property
    def type(self):
        """Gets the type of this SystemVolumeForCreateNodePoolInput.  # noqa: E501


        :return: The type of this SystemVolumeForCreateNodePoolInput.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this SystemVolumeForCreateNodePoolInput.


        :param type: The type of this SystemVolumeForCreateNodePoolInput.  # noqa: E501
        :type: str
        """
        allowed_values = ["ESSD_PL0", "ESSD_FlexPL"]  # noqa: E501
        if (self._configuration.client_side_validation and
                type not in allowed_values):
            raise ValueError(
                "Invalid value for `type` ({0}), must be one of {1}"  # noqa: E501
                .format(type, allowed_values)
            )

        self._type = type

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(SystemVolumeForCreateNodePoolInput, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, SystemVolumeForCreateNodePoolInput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SystemVolumeForCreateNodePoolInput):
            return True

        return self.to_dict() != other.to_dict()
