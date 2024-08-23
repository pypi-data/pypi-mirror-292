# coding: utf-8

"""
    rds_mysql_v2

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class ConfigInfoForDescribeTasksOutput(object):
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
        'config_info_key': 'str',
        'config_info_value': 'list[str]'
    }

    attribute_map = {
        'config_info_key': 'ConfigInfoKey',
        'config_info_value': 'ConfigInfoValue'
    }

    def __init__(self, config_info_key=None, config_info_value=None, _configuration=None):  # noqa: E501
        """ConfigInfoForDescribeTasksOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._config_info_key = None
        self._config_info_value = None
        self.discriminator = None

        if config_info_key is not None:
            self.config_info_key = config_info_key
        if config_info_value is not None:
            self.config_info_value = config_info_value

    @property
    def config_info_key(self):
        """Gets the config_info_key of this ConfigInfoForDescribeTasksOutput.  # noqa: E501


        :return: The config_info_key of this ConfigInfoForDescribeTasksOutput.  # noqa: E501
        :rtype: str
        """
        return self._config_info_key

    @config_info_key.setter
    def config_info_key(self, config_info_key):
        """Sets the config_info_key of this ConfigInfoForDescribeTasksOutput.


        :param config_info_key: The config_info_key of this ConfigInfoForDescribeTasksOutput.  # noqa: E501
        :type: str
        """

        self._config_info_key = config_info_key

    @property
    def config_info_value(self):
        """Gets the config_info_value of this ConfigInfoForDescribeTasksOutput.  # noqa: E501


        :return: The config_info_value of this ConfigInfoForDescribeTasksOutput.  # noqa: E501
        :rtype: list[str]
        """
        return self._config_info_value

    @config_info_value.setter
    def config_info_value(self, config_info_value):
        """Sets the config_info_value of this ConfigInfoForDescribeTasksOutput.


        :param config_info_value: The config_info_value of this ConfigInfoForDescribeTasksOutput.  # noqa: E501
        :type: list[str]
        """

        self._config_info_value = config_info_value

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
        if issubclass(ConfigInfoForDescribeTasksOutput, dict):
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
        if not isinstance(other, ConfigInfoForDescribeTasksOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ConfigInfoForDescribeTasksOutput):
            return True

        return self.to_dict() != other.to_dict()
