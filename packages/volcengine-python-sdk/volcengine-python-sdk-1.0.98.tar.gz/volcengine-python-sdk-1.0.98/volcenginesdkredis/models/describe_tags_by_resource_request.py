# coding: utf-8

"""
    redis

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class DescribeTagsByResourceRequest(object):
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
        'instance_ids': 'list[str]',
        'page_number': 'int',
        'page_size': 'int',
        'tag_filters': 'list[TagFilterForDescribeTagsByResourceInput]'
    }

    attribute_map = {
        'instance_ids': 'InstanceIds',
        'page_number': 'PageNumber',
        'page_size': 'PageSize',
        'tag_filters': 'TagFilters'
    }

    def __init__(self, instance_ids=None, page_number=None, page_size=None, tag_filters=None, _configuration=None):  # noqa: E501
        """DescribeTagsByResourceRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._instance_ids = None
        self._page_number = None
        self._page_size = None
        self._tag_filters = None
        self.discriminator = None

        if instance_ids is not None:
            self.instance_ids = instance_ids
        self.page_number = page_number
        self.page_size = page_size
        if tag_filters is not None:
            self.tag_filters = tag_filters

    @property
    def instance_ids(self):
        """Gets the instance_ids of this DescribeTagsByResourceRequest.  # noqa: E501


        :return: The instance_ids of this DescribeTagsByResourceRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._instance_ids

    @instance_ids.setter
    def instance_ids(self, instance_ids):
        """Sets the instance_ids of this DescribeTagsByResourceRequest.


        :param instance_ids: The instance_ids of this DescribeTagsByResourceRequest.  # noqa: E501
        :type: list[str]
        """

        self._instance_ids = instance_ids

    @property
    def page_number(self):
        """Gets the page_number of this DescribeTagsByResourceRequest.  # noqa: E501


        :return: The page_number of this DescribeTagsByResourceRequest.  # noqa: E501
        :rtype: int
        """
        return self._page_number

    @page_number.setter
    def page_number(self, page_number):
        """Sets the page_number of this DescribeTagsByResourceRequest.


        :param page_number: The page_number of this DescribeTagsByResourceRequest.  # noqa: E501
        :type: int
        """
        if self._configuration.client_side_validation and page_number is None:
            raise ValueError("Invalid value for `page_number`, must not be `None`")  # noqa: E501

        self._page_number = page_number

    @property
    def page_size(self):
        """Gets the page_size of this DescribeTagsByResourceRequest.  # noqa: E501


        :return: The page_size of this DescribeTagsByResourceRequest.  # noqa: E501
        :rtype: int
        """
        return self._page_size

    @page_size.setter
    def page_size(self, page_size):
        """Sets the page_size of this DescribeTagsByResourceRequest.


        :param page_size: The page_size of this DescribeTagsByResourceRequest.  # noqa: E501
        :type: int
        """
        if self._configuration.client_side_validation and page_size is None:
            raise ValueError("Invalid value for `page_size`, must not be `None`")  # noqa: E501

        self._page_size = page_size

    @property
    def tag_filters(self):
        """Gets the tag_filters of this DescribeTagsByResourceRequest.  # noqa: E501


        :return: The tag_filters of this DescribeTagsByResourceRequest.  # noqa: E501
        :rtype: list[TagFilterForDescribeTagsByResourceInput]
        """
        return self._tag_filters

    @tag_filters.setter
    def tag_filters(self, tag_filters):
        """Sets the tag_filters of this DescribeTagsByResourceRequest.


        :param tag_filters: The tag_filters of this DescribeTagsByResourceRequest.  # noqa: E501
        :type: list[TagFilterForDescribeTagsByResourceInput]
        """

        self._tag_filters = tag_filters

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
        if issubclass(DescribeTagsByResourceRequest, dict):
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
        if not isinstance(other, DescribeTagsByResourceRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DescribeTagsByResourceRequest):
            return True

        return self.to_dict() != other.to_dict()
