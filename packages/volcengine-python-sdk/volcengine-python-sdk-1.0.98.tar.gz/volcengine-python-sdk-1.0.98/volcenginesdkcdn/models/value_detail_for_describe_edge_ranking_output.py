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


class ValueDetailForDescribeEdgeRankingOutput(object):
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
        'item_key': 'str',
        'ratio': 'float',
        'timestamp': 'int',
        'value': 'float'
    }

    attribute_map = {
        'item_key': 'ItemKey',
        'ratio': 'Ratio',
        'timestamp': 'Timestamp',
        'value': 'Value'
    }

    def __init__(self, item_key=None, ratio=None, timestamp=None, value=None, _configuration=None):  # noqa: E501
        """ValueDetailForDescribeEdgeRankingOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._item_key = None
        self._ratio = None
        self._timestamp = None
        self._value = None
        self.discriminator = None

        if item_key is not None:
            self.item_key = item_key
        if ratio is not None:
            self.ratio = ratio
        if timestamp is not None:
            self.timestamp = timestamp
        if value is not None:
            self.value = value

    @property
    def item_key(self):
        """Gets the item_key of this ValueDetailForDescribeEdgeRankingOutput.  # noqa: E501


        :return: The item_key of this ValueDetailForDescribeEdgeRankingOutput.  # noqa: E501
        :rtype: str
        """
        return self._item_key

    @item_key.setter
    def item_key(self, item_key):
        """Sets the item_key of this ValueDetailForDescribeEdgeRankingOutput.


        :param item_key: The item_key of this ValueDetailForDescribeEdgeRankingOutput.  # noqa: E501
        :type: str
        """

        self._item_key = item_key

    @property
    def ratio(self):
        """Gets the ratio of this ValueDetailForDescribeEdgeRankingOutput.  # noqa: E501


        :return: The ratio of this ValueDetailForDescribeEdgeRankingOutput.  # noqa: E501
        :rtype: float
        """
        return self._ratio

    @ratio.setter
    def ratio(self, ratio):
        """Sets the ratio of this ValueDetailForDescribeEdgeRankingOutput.


        :param ratio: The ratio of this ValueDetailForDescribeEdgeRankingOutput.  # noqa: E501
        :type: float
        """

        self._ratio = ratio

    @property
    def timestamp(self):
        """Gets the timestamp of this ValueDetailForDescribeEdgeRankingOutput.  # noqa: E501


        :return: The timestamp of this ValueDetailForDescribeEdgeRankingOutput.  # noqa: E501
        :rtype: int
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        """Sets the timestamp of this ValueDetailForDescribeEdgeRankingOutput.


        :param timestamp: The timestamp of this ValueDetailForDescribeEdgeRankingOutput.  # noqa: E501
        :type: int
        """

        self._timestamp = timestamp

    @property
    def value(self):
        """Gets the value of this ValueDetailForDescribeEdgeRankingOutput.  # noqa: E501


        :return: The value of this ValueDetailForDescribeEdgeRankingOutput.  # noqa: E501
        :rtype: float
        """
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value of this ValueDetailForDescribeEdgeRankingOutput.


        :param value: The value of this ValueDetailForDescribeEdgeRankingOutput.  # noqa: E501
        :type: float
        """

        self._value = value

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
        if issubclass(ValueDetailForDescribeEdgeRankingOutput, dict):
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
        if not isinstance(other, ValueDetailForDescribeEdgeRankingOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ValueDetailForDescribeEdgeRankingOutput):
            return True

        return self.to_dict() != other.to_dict()
