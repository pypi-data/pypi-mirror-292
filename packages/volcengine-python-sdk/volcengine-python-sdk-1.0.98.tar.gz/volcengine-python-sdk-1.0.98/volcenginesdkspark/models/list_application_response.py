# coding: utf-8

"""
    spark

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class ListApplicationResponse(object):
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
        'current': 'str',
        'page_size': 'str',
        'records': 'list[RecordForlistApplicationOutput]',
        'total': 'str'
    }

    attribute_map = {
        'current': 'Current',
        'page_size': 'PageSize',
        'records': 'Records',
        'total': 'Total'
    }

    def __init__(self, current=None, page_size=None, records=None, total=None, _configuration=None):  # noqa: E501
        """ListApplicationResponse - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._current = None
        self._page_size = None
        self._records = None
        self._total = None
        self.discriminator = None

        if current is not None:
            self.current = current
        if page_size is not None:
            self.page_size = page_size
        if records is not None:
            self.records = records
        if total is not None:
            self.total = total

    @property
    def current(self):
        """Gets the current of this ListApplicationResponse.  # noqa: E501


        :return: The current of this ListApplicationResponse.  # noqa: E501
        :rtype: str
        """
        return self._current

    @current.setter
    def current(self, current):
        """Sets the current of this ListApplicationResponse.


        :param current: The current of this ListApplicationResponse.  # noqa: E501
        :type: str
        """

        self._current = current

    @property
    def page_size(self):
        """Gets the page_size of this ListApplicationResponse.  # noqa: E501


        :return: The page_size of this ListApplicationResponse.  # noqa: E501
        :rtype: str
        """
        return self._page_size

    @page_size.setter
    def page_size(self, page_size):
        """Sets the page_size of this ListApplicationResponse.


        :param page_size: The page_size of this ListApplicationResponse.  # noqa: E501
        :type: str
        """

        self._page_size = page_size

    @property
    def records(self):
        """Gets the records of this ListApplicationResponse.  # noqa: E501


        :return: The records of this ListApplicationResponse.  # noqa: E501
        :rtype: list[RecordForlistApplicationOutput]
        """
        return self._records

    @records.setter
    def records(self, records):
        """Sets the records of this ListApplicationResponse.


        :param records: The records of this ListApplicationResponse.  # noqa: E501
        :type: list[RecordForlistApplicationOutput]
        """

        self._records = records

    @property
    def total(self):
        """Gets the total of this ListApplicationResponse.  # noqa: E501


        :return: The total of this ListApplicationResponse.  # noqa: E501
        :rtype: str
        """
        return self._total

    @total.setter
    def total(self, total):
        """Sets the total of this ListApplicationResponse.


        :param total: The total of this ListApplicationResponse.  # noqa: E501
        :type: str
        """

        self._total = total

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
        if issubclass(ListApplicationResponse, dict):
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
        if not isinstance(other, ListApplicationResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ListApplicationResponse):
            return True

        return self.to_dict() != other.to_dict()
