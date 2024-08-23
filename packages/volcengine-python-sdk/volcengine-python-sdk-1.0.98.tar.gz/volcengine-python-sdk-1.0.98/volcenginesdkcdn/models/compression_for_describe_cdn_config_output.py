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


class CompressionForDescribeCdnConfigOutput(object):
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
        'compression_rules': 'list[CompressionRuleForDescribeCdnConfigOutput]',
        'switch': 'bool'
    }

    attribute_map = {
        'compression_rules': 'CompressionRules',
        'switch': 'Switch'
    }

    def __init__(self, compression_rules=None, switch=None, _configuration=None):  # noqa: E501
        """CompressionForDescribeCdnConfigOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._compression_rules = None
        self._switch = None
        self.discriminator = None

        if compression_rules is not None:
            self.compression_rules = compression_rules
        if switch is not None:
            self.switch = switch

    @property
    def compression_rules(self):
        """Gets the compression_rules of this CompressionForDescribeCdnConfigOutput.  # noqa: E501


        :return: The compression_rules of this CompressionForDescribeCdnConfigOutput.  # noqa: E501
        :rtype: list[CompressionRuleForDescribeCdnConfigOutput]
        """
        return self._compression_rules

    @compression_rules.setter
    def compression_rules(self, compression_rules):
        """Sets the compression_rules of this CompressionForDescribeCdnConfigOutput.


        :param compression_rules: The compression_rules of this CompressionForDescribeCdnConfigOutput.  # noqa: E501
        :type: list[CompressionRuleForDescribeCdnConfigOutput]
        """

        self._compression_rules = compression_rules

    @property
    def switch(self):
        """Gets the switch of this CompressionForDescribeCdnConfigOutput.  # noqa: E501


        :return: The switch of this CompressionForDescribeCdnConfigOutput.  # noqa: E501
        :rtype: bool
        """
        return self._switch

    @switch.setter
    def switch(self, switch):
        """Sets the switch of this CompressionForDescribeCdnConfigOutput.


        :param switch: The switch of this CompressionForDescribeCdnConfigOutput.  # noqa: E501
        :type: bool
        """

        self._switch = switch

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
        if issubclass(CompressionForDescribeCdnConfigOutput, dict):
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
        if not isinstance(other, CompressionForDescribeCdnConfigOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CompressionForDescribeCdnConfigOutput):
            return True

        return self.to_dict() != other.to_dict()
