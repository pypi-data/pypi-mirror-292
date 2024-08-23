# coding: utf-8

"""
    mcdn

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class ListDnsSchedulesResponse(object):
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
        'dns_schedules': 'list[DnsScheduleForListDnsSchedulesOutput]',
        'pagination': 'PaginationForListDnsSchedulesOutput'
    }

    attribute_map = {
        'dns_schedules': 'DnsSchedules',
        'pagination': 'Pagination'
    }

    def __init__(self, dns_schedules=None, pagination=None, _configuration=None):  # noqa: E501
        """ListDnsSchedulesResponse - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._dns_schedules = None
        self._pagination = None
        self.discriminator = None

        if dns_schedules is not None:
            self.dns_schedules = dns_schedules
        if pagination is not None:
            self.pagination = pagination

    @property
    def dns_schedules(self):
        """Gets the dns_schedules of this ListDnsSchedulesResponse.  # noqa: E501


        :return: The dns_schedules of this ListDnsSchedulesResponse.  # noqa: E501
        :rtype: list[DnsScheduleForListDnsSchedulesOutput]
        """
        return self._dns_schedules

    @dns_schedules.setter
    def dns_schedules(self, dns_schedules):
        """Sets the dns_schedules of this ListDnsSchedulesResponse.


        :param dns_schedules: The dns_schedules of this ListDnsSchedulesResponse.  # noqa: E501
        :type: list[DnsScheduleForListDnsSchedulesOutput]
        """

        self._dns_schedules = dns_schedules

    @property
    def pagination(self):
        """Gets the pagination of this ListDnsSchedulesResponse.  # noqa: E501


        :return: The pagination of this ListDnsSchedulesResponse.  # noqa: E501
        :rtype: PaginationForListDnsSchedulesOutput
        """
        return self._pagination

    @pagination.setter
    def pagination(self, pagination):
        """Sets the pagination of this ListDnsSchedulesResponse.


        :param pagination: The pagination of this ListDnsSchedulesResponse.  # noqa: E501
        :type: PaginationForListDnsSchedulesOutput
        """

        self._pagination = pagination

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
        if issubclass(ListDnsSchedulesResponse, dict):
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
        if not isinstance(other, ListDnsSchedulesResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ListDnsSchedulesResponse):
            return True

        return self.to_dict() != other.to_dict()
