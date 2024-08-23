# coding: utf-8

"""
    cdn

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class AuthModeConfigForDescribeCdnConfigOutput(object):
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
        'backup_remote_addr': 'str',
        'master_remote_addr': 'str',
        'path_type': 'str',
        'path_value': 'str',
        'request_method': 'str'
    }

    attribute_map = {
        'backup_remote_addr': 'BackupRemoteAddr',
        'master_remote_addr': 'MasterRemoteAddr',
        'path_type': 'PathType',
        'path_value': 'PathValue',
        'request_method': 'RequestMethod'
    }

    def __init__(self, backup_remote_addr=None, master_remote_addr=None, path_type=None, path_value=None, request_method=None, _configuration=None):  # noqa: E501
        """AuthModeConfigForDescribeCdnConfigOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._backup_remote_addr = None
        self._master_remote_addr = None
        self._path_type = None
        self._path_value = None
        self._request_method = None
        self.discriminator = None

        if backup_remote_addr is not None:
            self.backup_remote_addr = backup_remote_addr
        if master_remote_addr is not None:
            self.master_remote_addr = master_remote_addr
        if path_type is not None:
            self.path_type = path_type
        if path_value is not None:
            self.path_value = path_value
        if request_method is not None:
            self.request_method = request_method

    @property
    def backup_remote_addr(self):
        """Gets the backup_remote_addr of this AuthModeConfigForDescribeCdnConfigOutput.  # noqa: E501


        :return: The backup_remote_addr of this AuthModeConfigForDescribeCdnConfigOutput.  # noqa: E501
        :rtype: str
        """
        return self._backup_remote_addr

    @backup_remote_addr.setter
    def backup_remote_addr(self, backup_remote_addr):
        """Sets the backup_remote_addr of this AuthModeConfigForDescribeCdnConfigOutput.


        :param backup_remote_addr: The backup_remote_addr of this AuthModeConfigForDescribeCdnConfigOutput.  # noqa: E501
        :type: str
        """

        self._backup_remote_addr = backup_remote_addr

    @property
    def master_remote_addr(self):
        """Gets the master_remote_addr of this AuthModeConfigForDescribeCdnConfigOutput.  # noqa: E501


        :return: The master_remote_addr of this AuthModeConfigForDescribeCdnConfigOutput.  # noqa: E501
        :rtype: str
        """
        return self._master_remote_addr

    @master_remote_addr.setter
    def master_remote_addr(self, master_remote_addr):
        """Sets the master_remote_addr of this AuthModeConfigForDescribeCdnConfigOutput.


        :param master_remote_addr: The master_remote_addr of this AuthModeConfigForDescribeCdnConfigOutput.  # noqa: E501
        :type: str
        """

        self._master_remote_addr = master_remote_addr

    @property
    def path_type(self):
        """Gets the path_type of this AuthModeConfigForDescribeCdnConfigOutput.  # noqa: E501


        :return: The path_type of this AuthModeConfigForDescribeCdnConfigOutput.  # noqa: E501
        :rtype: str
        """
        return self._path_type

    @path_type.setter
    def path_type(self, path_type):
        """Sets the path_type of this AuthModeConfigForDescribeCdnConfigOutput.


        :param path_type: The path_type of this AuthModeConfigForDescribeCdnConfigOutput.  # noqa: E501
        :type: str
        """

        self._path_type = path_type

    @property
    def path_value(self):
        """Gets the path_value of this AuthModeConfigForDescribeCdnConfigOutput.  # noqa: E501


        :return: The path_value of this AuthModeConfigForDescribeCdnConfigOutput.  # noqa: E501
        :rtype: str
        """
        return self._path_value

    @path_value.setter
    def path_value(self, path_value):
        """Sets the path_value of this AuthModeConfigForDescribeCdnConfigOutput.


        :param path_value: The path_value of this AuthModeConfigForDescribeCdnConfigOutput.  # noqa: E501
        :type: str
        """

        self._path_value = path_value

    @property
    def request_method(self):
        """Gets the request_method of this AuthModeConfigForDescribeCdnConfigOutput.  # noqa: E501


        :return: The request_method of this AuthModeConfigForDescribeCdnConfigOutput.  # noqa: E501
        :rtype: str
        """
        return self._request_method

    @request_method.setter
    def request_method(self, request_method):
        """Sets the request_method of this AuthModeConfigForDescribeCdnConfigOutput.


        :param request_method: The request_method of this AuthModeConfigForDescribeCdnConfigOutput.  # noqa: E501
        :type: str
        """

        self._request_method = request_method

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
        if issubclass(AuthModeConfigForDescribeCdnConfigOutput, dict):
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
        if not isinstance(other, AuthModeConfigForDescribeCdnConfigOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AuthModeConfigForDescribeCdnConfigOutput):
            return True

        return self.to_dict() != other.to_dict()
