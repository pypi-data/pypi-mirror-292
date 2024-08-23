# coding: utf-8

"""
    cen

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class DescribeCenInterRegionBandwidthsResponse(object):
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
        'inter_region_bandwidths': 'list[InterRegionBandwidthForDescribeCenInterRegionBandwidthsOutput]',
        'page_number': 'int',
        'page_size': 'int',
        'request_id': 'str',
        'total_count': 'int'
    }

    attribute_map = {
        'inter_region_bandwidths': 'InterRegionBandwidths',
        'page_number': 'PageNumber',
        'page_size': 'PageSize',
        'request_id': 'RequestId',
        'total_count': 'TotalCount'
    }

    def __init__(self, inter_region_bandwidths=None, page_number=None, page_size=None, request_id=None, total_count=None, _configuration=None):  # noqa: E501
        """DescribeCenInterRegionBandwidthsResponse - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._inter_region_bandwidths = None
        self._page_number = None
        self._page_size = None
        self._request_id = None
        self._total_count = None
        self.discriminator = None

        if inter_region_bandwidths is not None:
            self.inter_region_bandwidths = inter_region_bandwidths
        if page_number is not None:
            self.page_number = page_number
        if page_size is not None:
            self.page_size = page_size
        if request_id is not None:
            self.request_id = request_id
        if total_count is not None:
            self.total_count = total_count

    @property
    def inter_region_bandwidths(self):
        """Gets the inter_region_bandwidths of this DescribeCenInterRegionBandwidthsResponse.  # noqa: E501


        :return: The inter_region_bandwidths of this DescribeCenInterRegionBandwidthsResponse.  # noqa: E501
        :rtype: list[InterRegionBandwidthForDescribeCenInterRegionBandwidthsOutput]
        """
        return self._inter_region_bandwidths

    @inter_region_bandwidths.setter
    def inter_region_bandwidths(self, inter_region_bandwidths):
        """Sets the inter_region_bandwidths of this DescribeCenInterRegionBandwidthsResponse.


        :param inter_region_bandwidths: The inter_region_bandwidths of this DescribeCenInterRegionBandwidthsResponse.  # noqa: E501
        :type: list[InterRegionBandwidthForDescribeCenInterRegionBandwidthsOutput]
        """

        self._inter_region_bandwidths = inter_region_bandwidths

    @property
    def page_number(self):
        """Gets the page_number of this DescribeCenInterRegionBandwidthsResponse.  # noqa: E501


        :return: The page_number of this DescribeCenInterRegionBandwidthsResponse.  # noqa: E501
        :rtype: int
        """
        return self._page_number

    @page_number.setter
    def page_number(self, page_number):
        """Sets the page_number of this DescribeCenInterRegionBandwidthsResponse.


        :param page_number: The page_number of this DescribeCenInterRegionBandwidthsResponse.  # noqa: E501
        :type: int
        """

        self._page_number = page_number

    @property
    def page_size(self):
        """Gets the page_size of this DescribeCenInterRegionBandwidthsResponse.  # noqa: E501


        :return: The page_size of this DescribeCenInterRegionBandwidthsResponse.  # noqa: E501
        :rtype: int
        """
        return self._page_size

    @page_size.setter
    def page_size(self, page_size):
        """Sets the page_size of this DescribeCenInterRegionBandwidthsResponse.


        :param page_size: The page_size of this DescribeCenInterRegionBandwidthsResponse.  # noqa: E501
        :type: int
        """

        self._page_size = page_size

    @property
    def request_id(self):
        """Gets the request_id of this DescribeCenInterRegionBandwidthsResponse.  # noqa: E501


        :return: The request_id of this DescribeCenInterRegionBandwidthsResponse.  # noqa: E501
        :rtype: str
        """
        return self._request_id

    @request_id.setter
    def request_id(self, request_id):
        """Sets the request_id of this DescribeCenInterRegionBandwidthsResponse.


        :param request_id: The request_id of this DescribeCenInterRegionBandwidthsResponse.  # noqa: E501
        :type: str
        """

        self._request_id = request_id

    @property
    def total_count(self):
        """Gets the total_count of this DescribeCenInterRegionBandwidthsResponse.  # noqa: E501


        :return: The total_count of this DescribeCenInterRegionBandwidthsResponse.  # noqa: E501
        :rtype: int
        """
        return self._total_count

    @total_count.setter
    def total_count(self, total_count):
        """Sets the total_count of this DescribeCenInterRegionBandwidthsResponse.


        :param total_count: The total_count of this DescribeCenInterRegionBandwidthsResponse.  # noqa: E501
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
        if issubclass(DescribeCenInterRegionBandwidthsResponse, dict):
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
        if not isinstance(other, DescribeCenInterRegionBandwidthsResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DescribeCenInterRegionBandwidthsResponse):
            return True

        return self.to_dict() != other.to_dict()
