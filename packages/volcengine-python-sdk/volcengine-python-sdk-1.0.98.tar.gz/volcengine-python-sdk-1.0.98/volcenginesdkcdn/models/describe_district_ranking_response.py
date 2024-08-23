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


class DescribeDistrictRankingResponse(object):
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
        'item': 'str',
        'top_data_details': 'list[TopDataDetailForDescribeDistrictRankingOutput]'
    }

    attribute_map = {
        'item': 'Item',
        'top_data_details': 'TopDataDetails'
    }

    def __init__(self, item=None, top_data_details=None, _configuration=None):  # noqa: E501
        """DescribeDistrictRankingResponse - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._item = None
        self._top_data_details = None
        self.discriminator = None

        if item is not None:
            self.item = item
        if top_data_details is not None:
            self.top_data_details = top_data_details

    @property
    def item(self):
        """Gets the item of this DescribeDistrictRankingResponse.  # noqa: E501


        :return: The item of this DescribeDistrictRankingResponse.  # noqa: E501
        :rtype: str
        """
        return self._item

    @item.setter
    def item(self, item):
        """Sets the item of this DescribeDistrictRankingResponse.


        :param item: The item of this DescribeDistrictRankingResponse.  # noqa: E501
        :type: str
        """

        self._item = item

    @property
    def top_data_details(self):
        """Gets the top_data_details of this DescribeDistrictRankingResponse.  # noqa: E501


        :return: The top_data_details of this DescribeDistrictRankingResponse.  # noqa: E501
        :rtype: list[TopDataDetailForDescribeDistrictRankingOutput]
        """
        return self._top_data_details

    @top_data_details.setter
    def top_data_details(self, top_data_details):
        """Sets the top_data_details of this DescribeDistrictRankingResponse.


        :param top_data_details: The top_data_details of this DescribeDistrictRankingResponse.  # noqa: E501
        :type: list[TopDataDetailForDescribeDistrictRankingOutput]
        """

        self._top_data_details = top_data_details

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
        if issubclass(DescribeDistrictRankingResponse, dict):
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
        if not isinstance(other, DescribeDistrictRankingResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DescribeDistrictRankingResponse):
            return True

        return self.to_dict() != other.to_dict()
