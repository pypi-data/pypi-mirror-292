# coding: utf-8

"""
    waf

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class ListBlockRuleResponse(object):
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
        'count': 'int',
        'current_page': 'int',
        'data': 'list[DataForListBlockRuleOutput]',
        'page_size': 'int',
        'total_count': 'int'
    }

    attribute_map = {
        'count': 'Count',
        'current_page': 'CurrentPage',
        'data': 'Data',
        'page_size': 'PageSize',
        'total_count': 'TotalCount'
    }

    def __init__(self, count=None, current_page=None, data=None, page_size=None, total_count=None, _configuration=None):  # noqa: E501
        """ListBlockRuleResponse - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._count = None
        self._current_page = None
        self._data = None
        self._page_size = None
        self._total_count = None
        self.discriminator = None

        if count is not None:
            self.count = count
        if current_page is not None:
            self.current_page = current_page
        if data is not None:
            self.data = data
        if page_size is not None:
            self.page_size = page_size
        if total_count is not None:
            self.total_count = total_count

    @property
    def count(self):
        """Gets the count of this ListBlockRuleResponse.  # noqa: E501


        :return: The count of this ListBlockRuleResponse.  # noqa: E501
        :rtype: int
        """
        return self._count

    @count.setter
    def count(self, count):
        """Sets the count of this ListBlockRuleResponse.


        :param count: The count of this ListBlockRuleResponse.  # noqa: E501
        :type: int
        """

        self._count = count

    @property
    def current_page(self):
        """Gets the current_page of this ListBlockRuleResponse.  # noqa: E501


        :return: The current_page of this ListBlockRuleResponse.  # noqa: E501
        :rtype: int
        """
        return self._current_page

    @current_page.setter
    def current_page(self, current_page):
        """Sets the current_page of this ListBlockRuleResponse.


        :param current_page: The current_page of this ListBlockRuleResponse.  # noqa: E501
        :type: int
        """

        self._current_page = current_page

    @property
    def data(self):
        """Gets the data of this ListBlockRuleResponse.  # noqa: E501


        :return: The data of this ListBlockRuleResponse.  # noqa: E501
        :rtype: list[DataForListBlockRuleOutput]
        """
        return self._data

    @data.setter
    def data(self, data):
        """Sets the data of this ListBlockRuleResponse.


        :param data: The data of this ListBlockRuleResponse.  # noqa: E501
        :type: list[DataForListBlockRuleOutput]
        """

        self._data = data

    @property
    def page_size(self):
        """Gets the page_size of this ListBlockRuleResponse.  # noqa: E501


        :return: The page_size of this ListBlockRuleResponse.  # noqa: E501
        :rtype: int
        """
        return self._page_size

    @page_size.setter
    def page_size(self, page_size):
        """Sets the page_size of this ListBlockRuleResponse.


        :param page_size: The page_size of this ListBlockRuleResponse.  # noqa: E501
        :type: int
        """

        self._page_size = page_size

    @property
    def total_count(self):
        """Gets the total_count of this ListBlockRuleResponse.  # noqa: E501


        :return: The total_count of this ListBlockRuleResponse.  # noqa: E501
        :rtype: int
        """
        return self._total_count

    @total_count.setter
    def total_count(self, total_count):
        """Sets the total_count of this ListBlockRuleResponse.


        :param total_count: The total_count of this ListBlockRuleResponse.  # noqa: E501
        :type: int
        """

        self._total_count = total_count

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
        if issubclass(ListBlockRuleResponse, dict):
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
        if not isinstance(other, ListBlockRuleResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ListBlockRuleResponse):
            return True

        return self.to_dict() != other.to_dict()
