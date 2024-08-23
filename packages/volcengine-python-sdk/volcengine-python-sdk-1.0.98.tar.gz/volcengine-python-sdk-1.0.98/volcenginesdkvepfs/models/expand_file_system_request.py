# coding: utf-8

"""
    vepfs

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class ExpandFileSystemRequest(object):
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
        'capacity': 'int',
        'enable_restripe': 'bool',
        'file_system_id': 'str'
    }

    attribute_map = {
        'capacity': 'Capacity',
        'enable_restripe': 'EnableRestripe',
        'file_system_id': 'FileSystemId'
    }

    def __init__(self, capacity=None, enable_restripe=None, file_system_id=None, _configuration=None):  # noqa: E501
        """ExpandFileSystemRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._capacity = None
        self._enable_restripe = None
        self._file_system_id = None
        self.discriminator = None

        if capacity is not None:
            self.capacity = capacity
        if enable_restripe is not None:
            self.enable_restripe = enable_restripe
        if file_system_id is not None:
            self.file_system_id = file_system_id

    @property
    def capacity(self):
        """Gets the capacity of this ExpandFileSystemRequest.  # noqa: E501


        :return: The capacity of this ExpandFileSystemRequest.  # noqa: E501
        :rtype: int
        """
        return self._capacity

    @capacity.setter
    def capacity(self, capacity):
        """Sets the capacity of this ExpandFileSystemRequest.


        :param capacity: The capacity of this ExpandFileSystemRequest.  # noqa: E501
        :type: int
        """

        self._capacity = capacity

    @property
    def enable_restripe(self):
        """Gets the enable_restripe of this ExpandFileSystemRequest.  # noqa: E501


        :return: The enable_restripe of this ExpandFileSystemRequest.  # noqa: E501
        :rtype: bool
        """
        return self._enable_restripe

    @enable_restripe.setter
    def enable_restripe(self, enable_restripe):
        """Sets the enable_restripe of this ExpandFileSystemRequest.


        :param enable_restripe: The enable_restripe of this ExpandFileSystemRequest.  # noqa: E501
        :type: bool
        """

        self._enable_restripe = enable_restripe

    @property
    def file_system_id(self):
        """Gets the file_system_id of this ExpandFileSystemRequest.  # noqa: E501


        :return: The file_system_id of this ExpandFileSystemRequest.  # noqa: E501
        :rtype: str
        """
        return self._file_system_id

    @file_system_id.setter
    def file_system_id(self, file_system_id):
        """Sets the file_system_id of this ExpandFileSystemRequest.


        :param file_system_id: The file_system_id of this ExpandFileSystemRequest.  # noqa: E501
        :type: str
        """

        self._file_system_id = file_system_id

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
        if issubclass(ExpandFileSystemRequest, dict):
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
        if not isinstance(other, ExpandFileSystemRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ExpandFileSystemRequest):
            return True

        return self.to_dict() != other.to_dict()
