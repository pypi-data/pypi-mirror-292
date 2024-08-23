# coding: utf-8

"""
    vpn

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class DescribeVpnGatewaysBillingRequest(object):
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
        'vpn_gateway_ids': 'list[str]'
    }

    attribute_map = {
        'page_number': 'PageNumber',
        'page_size': 'PageSize',
        'vpn_gateway_ids': 'VpnGatewayIds'
    }

    def __init__(self, page_number=None, page_size=None, vpn_gateway_ids=None, _configuration=None):  # noqa: E501
        """DescribeVpnGatewaysBillingRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._page_number = None
        self._page_size = None
        self._vpn_gateway_ids = None
        self.discriminator = None

        if page_number is not None:
            self.page_number = page_number
        if page_size is not None:
            self.page_size = page_size
        if vpn_gateway_ids is not None:
            self.vpn_gateway_ids = vpn_gateway_ids

    @property
    def page_number(self):
        """Gets the page_number of this DescribeVpnGatewaysBillingRequest.  # noqa: E501


        :return: The page_number of this DescribeVpnGatewaysBillingRequest.  # noqa: E501
        :rtype: int
        """
        return self._page_number

    @page_number.setter
    def page_number(self, page_number):
        """Sets the page_number of this DescribeVpnGatewaysBillingRequest.


        :param page_number: The page_number of this DescribeVpnGatewaysBillingRequest.  # noqa: E501
        :type: int
        """

        self._page_number = page_number

    @property
    def page_size(self):
        """Gets the page_size of this DescribeVpnGatewaysBillingRequest.  # noqa: E501


        :return: The page_size of this DescribeVpnGatewaysBillingRequest.  # noqa: E501
        :rtype: int
        """
        return self._page_size

    @page_size.setter
    def page_size(self, page_size):
        """Sets the page_size of this DescribeVpnGatewaysBillingRequest.


        :param page_size: The page_size of this DescribeVpnGatewaysBillingRequest.  # noqa: E501
        :type: int
        """
        if (self._configuration.client_side_validation and
                page_size is not None and page_size > 100):  # noqa: E501
            raise ValueError("Invalid value for `page_size`, must be a value less than or equal to `100`")  # noqa: E501

        self._page_size = page_size

    @property
    def vpn_gateway_ids(self):
        """Gets the vpn_gateway_ids of this DescribeVpnGatewaysBillingRequest.  # noqa: E501


        :return: The vpn_gateway_ids of this DescribeVpnGatewaysBillingRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._vpn_gateway_ids

    @vpn_gateway_ids.setter
    def vpn_gateway_ids(self, vpn_gateway_ids):
        """Sets the vpn_gateway_ids of this DescribeVpnGatewaysBillingRequest.


        :param vpn_gateway_ids: The vpn_gateway_ids of this DescribeVpnGatewaysBillingRequest.  # noqa: E501
        :type: list[str]
        """

        self._vpn_gateway_ids = vpn_gateway_ids

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
        if issubclass(DescribeVpnGatewaysBillingRequest, dict):
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
        if not isinstance(other, DescribeVpnGatewaysBillingRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DescribeVpnGatewaysBillingRequest):
            return True

        return self.to_dict() != other.to_dict()
