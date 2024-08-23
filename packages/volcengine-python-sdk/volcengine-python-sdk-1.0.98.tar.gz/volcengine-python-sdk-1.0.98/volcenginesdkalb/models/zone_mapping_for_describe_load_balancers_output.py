# coding: utf-8

"""
    alb

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class ZoneMappingForDescribeLoadBalancersOutput(object):
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
        'load_balancer_addresses': 'list[LoadBalancerAddressForDescribeLoadBalancersOutput]',
        'subnet_id': 'str',
        'zone_id': 'str'
    }

    attribute_map = {
        'load_balancer_addresses': 'LoadBalancerAddresses',
        'subnet_id': 'SubnetId',
        'zone_id': 'ZoneId'
    }

    def __init__(self, load_balancer_addresses=None, subnet_id=None, zone_id=None, _configuration=None):  # noqa: E501
        """ZoneMappingForDescribeLoadBalancersOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._load_balancer_addresses = None
        self._subnet_id = None
        self._zone_id = None
        self.discriminator = None

        if load_balancer_addresses is not None:
            self.load_balancer_addresses = load_balancer_addresses
        if subnet_id is not None:
            self.subnet_id = subnet_id
        if zone_id is not None:
            self.zone_id = zone_id

    @property
    def load_balancer_addresses(self):
        """Gets the load_balancer_addresses of this ZoneMappingForDescribeLoadBalancersOutput.  # noqa: E501


        :return: The load_balancer_addresses of this ZoneMappingForDescribeLoadBalancersOutput.  # noqa: E501
        :rtype: list[LoadBalancerAddressForDescribeLoadBalancersOutput]
        """
        return self._load_balancer_addresses

    @load_balancer_addresses.setter
    def load_balancer_addresses(self, load_balancer_addresses):
        """Sets the load_balancer_addresses of this ZoneMappingForDescribeLoadBalancersOutput.


        :param load_balancer_addresses: The load_balancer_addresses of this ZoneMappingForDescribeLoadBalancersOutput.  # noqa: E501
        :type: list[LoadBalancerAddressForDescribeLoadBalancersOutput]
        """

        self._load_balancer_addresses = load_balancer_addresses

    @property
    def subnet_id(self):
        """Gets the subnet_id of this ZoneMappingForDescribeLoadBalancersOutput.  # noqa: E501


        :return: The subnet_id of this ZoneMappingForDescribeLoadBalancersOutput.  # noqa: E501
        :rtype: str
        """
        return self._subnet_id

    @subnet_id.setter
    def subnet_id(self, subnet_id):
        """Sets the subnet_id of this ZoneMappingForDescribeLoadBalancersOutput.


        :param subnet_id: The subnet_id of this ZoneMappingForDescribeLoadBalancersOutput.  # noqa: E501
        :type: str
        """

        self._subnet_id = subnet_id

    @property
    def zone_id(self):
        """Gets the zone_id of this ZoneMappingForDescribeLoadBalancersOutput.  # noqa: E501


        :return: The zone_id of this ZoneMappingForDescribeLoadBalancersOutput.  # noqa: E501
        :rtype: str
        """
        return self._zone_id

    @zone_id.setter
    def zone_id(self, zone_id):
        """Sets the zone_id of this ZoneMappingForDescribeLoadBalancersOutput.


        :param zone_id: The zone_id of this ZoneMappingForDescribeLoadBalancersOutput.  # noqa: E501
        :type: str
        """

        self._zone_id = zone_id

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
        if issubclass(ZoneMappingForDescribeLoadBalancersOutput, dict):
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
        if not isinstance(other, ZoneMappingForDescribeLoadBalancersOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ZoneMappingForDescribeLoadBalancersOutput):
            return True

        return self.to_dict() != other.to_dict()
