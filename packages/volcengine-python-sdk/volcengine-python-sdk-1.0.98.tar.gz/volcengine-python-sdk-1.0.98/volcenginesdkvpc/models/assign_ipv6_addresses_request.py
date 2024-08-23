# coding: utf-8

"""
    vpc

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class AssignIpv6AddressesRequest(object):
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
        'ipv6_address': 'list[str]',
        'ipv6_address_count': 'int',
        'network_interface_id': 'str'
    }

    attribute_map = {
        'ipv6_address': 'Ipv6Address',
        'ipv6_address_count': 'Ipv6AddressCount',
        'network_interface_id': 'NetworkInterfaceId'
    }

    def __init__(self, ipv6_address=None, ipv6_address_count=None, network_interface_id=None, _configuration=None):  # noqa: E501
        """AssignIpv6AddressesRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._ipv6_address = None
        self._ipv6_address_count = None
        self._network_interface_id = None
        self.discriminator = None

        if ipv6_address is not None:
            self.ipv6_address = ipv6_address
        if ipv6_address_count is not None:
            self.ipv6_address_count = ipv6_address_count
        self.network_interface_id = network_interface_id

    @property
    def ipv6_address(self):
        """Gets the ipv6_address of this AssignIpv6AddressesRequest.  # noqa: E501


        :return: The ipv6_address of this AssignIpv6AddressesRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._ipv6_address

    @ipv6_address.setter
    def ipv6_address(self, ipv6_address):
        """Sets the ipv6_address of this AssignIpv6AddressesRequest.


        :param ipv6_address: The ipv6_address of this AssignIpv6AddressesRequest.  # noqa: E501
        :type: list[str]
        """

        self._ipv6_address = ipv6_address

    @property
    def ipv6_address_count(self):
        """Gets the ipv6_address_count of this AssignIpv6AddressesRequest.  # noqa: E501


        :return: The ipv6_address_count of this AssignIpv6AddressesRequest.  # noqa: E501
        :rtype: int
        """
        return self._ipv6_address_count

    @ipv6_address_count.setter
    def ipv6_address_count(self, ipv6_address_count):
        """Sets the ipv6_address_count of this AssignIpv6AddressesRequest.


        :param ipv6_address_count: The ipv6_address_count of this AssignIpv6AddressesRequest.  # noqa: E501
        :type: int
        """

        self._ipv6_address_count = ipv6_address_count

    @property
    def network_interface_id(self):
        """Gets the network_interface_id of this AssignIpv6AddressesRequest.  # noqa: E501


        :return: The network_interface_id of this AssignIpv6AddressesRequest.  # noqa: E501
        :rtype: str
        """
        return self._network_interface_id

    @network_interface_id.setter
    def network_interface_id(self, network_interface_id):
        """Sets the network_interface_id of this AssignIpv6AddressesRequest.


        :param network_interface_id: The network_interface_id of this AssignIpv6AddressesRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and network_interface_id is None:
            raise ValueError("Invalid value for `network_interface_id`, must not be `None`")  # noqa: E501

        self._network_interface_id = network_interface_id

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
        if issubclass(AssignIpv6AddressesRequest, dict):
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
        if not isinstance(other, AssignIpv6AddressesRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AssignIpv6AddressesRequest):
            return True

        return self.to_dict() != other.to_dict()
