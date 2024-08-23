# coding: utf-8

"""
    clb

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class DescribeListenerHealthResponse(object):
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
        'page_number': 'int',
        'page_size': 'int',
        'request_id': 'str',
        'results': 'list[ResultForDescribeListenerHealthOutput]',
        'status': 'str',
        'total_count': 'int',
        'un_healthy_count': 'int'
    }

    attribute_map = {
        'page_number': 'PageNumber',
        'page_size': 'PageSize',
        'request_id': 'RequestId',
        'results': 'Results',
        'status': 'Status',
        'total_count': 'TotalCount',
        'un_healthy_count': 'UnHealthyCount'
    }

    def __init__(self, page_number=None, page_size=None, request_id=None, results=None, status=None, total_count=None, un_healthy_count=None, _configuration=None):  # noqa: E501
        """DescribeListenerHealthResponse - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._page_number = None
        self._page_size = None
        self._request_id = None
        self._results = None
        self._status = None
        self._total_count = None
        self._un_healthy_count = None
        self.discriminator = None

        if page_number is not None:
            self.page_number = page_number
        if page_size is not None:
            self.page_size = page_size
        if request_id is not None:
            self.request_id = request_id
        if results is not None:
            self.results = results
        if status is not None:
            self.status = status
        if total_count is not None:
            self.total_count = total_count
        if un_healthy_count is not None:
            self.un_healthy_count = un_healthy_count

    @property
    def page_number(self):
        """Gets the page_number of this DescribeListenerHealthResponse.  # noqa: E501


        :return: The page_number of this DescribeListenerHealthResponse.  # noqa: E501
        :rtype: int
        """
        return self._page_number

    @page_number.setter
    def page_number(self, page_number):
        """Sets the page_number of this DescribeListenerHealthResponse.


        :param page_number: The page_number of this DescribeListenerHealthResponse.  # noqa: E501
        :type: int
        """

        self._page_number = page_number

    @property
    def page_size(self):
        """Gets the page_size of this DescribeListenerHealthResponse.  # noqa: E501


        :return: The page_size of this DescribeListenerHealthResponse.  # noqa: E501
        :rtype: int
        """
        return self._page_size

    @page_size.setter
    def page_size(self, page_size):
        """Sets the page_size of this DescribeListenerHealthResponse.


        :param page_size: The page_size of this DescribeListenerHealthResponse.  # noqa: E501
        :type: int
        """

        self._page_size = page_size

    @property
    def request_id(self):
        """Gets the request_id of this DescribeListenerHealthResponse.  # noqa: E501


        :return: The request_id of this DescribeListenerHealthResponse.  # noqa: E501
        :rtype: str
        """
        return self._request_id

    @request_id.setter
    def request_id(self, request_id):
        """Sets the request_id of this DescribeListenerHealthResponse.


        :param request_id: The request_id of this DescribeListenerHealthResponse.  # noqa: E501
        :type: str
        """

        self._request_id = request_id

    @property
    def results(self):
        """Gets the results of this DescribeListenerHealthResponse.  # noqa: E501


        :return: The results of this DescribeListenerHealthResponse.  # noqa: E501
        :rtype: list[ResultForDescribeListenerHealthOutput]
        """
        return self._results

    @results.setter
    def results(self, results):
        """Sets the results of this DescribeListenerHealthResponse.


        :param results: The results of this DescribeListenerHealthResponse.  # noqa: E501
        :type: list[ResultForDescribeListenerHealthOutput]
        """

        self._results = results

    @property
    def status(self):
        """Gets the status of this DescribeListenerHealthResponse.  # noqa: E501


        :return: The status of this DescribeListenerHealthResponse.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this DescribeListenerHealthResponse.


        :param status: The status of this DescribeListenerHealthResponse.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def total_count(self):
        """Gets the total_count of this DescribeListenerHealthResponse.  # noqa: E501


        :return: The total_count of this DescribeListenerHealthResponse.  # noqa: E501
        :rtype: int
        """
        return self._total_count

    @total_count.setter
    def total_count(self, total_count):
        """Sets the total_count of this DescribeListenerHealthResponse.


        :param total_count: The total_count of this DescribeListenerHealthResponse.  # noqa: E501
        :type: int
        """

        self._total_count = total_count

    @property
    def un_healthy_count(self):
        """Gets the un_healthy_count of this DescribeListenerHealthResponse.  # noqa: E501


        :return: The un_healthy_count of this DescribeListenerHealthResponse.  # noqa: E501
        :rtype: int
        """
        return self._un_healthy_count

    @un_healthy_count.setter
    def un_healthy_count(self, un_healthy_count):
        """Sets the un_healthy_count of this DescribeListenerHealthResponse.


        :param un_healthy_count: The un_healthy_count of this DescribeListenerHealthResponse.  # noqa: E501
        :type: int
        """

        self._un_healthy_count = un_healthy_count

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
        if issubclass(DescribeListenerHealthResponse, dict):
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
        if not isinstance(other, DescribeListenerHealthResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DescribeListenerHealthResponse):
            return True

        return self.to_dict() != other.to_dict()
