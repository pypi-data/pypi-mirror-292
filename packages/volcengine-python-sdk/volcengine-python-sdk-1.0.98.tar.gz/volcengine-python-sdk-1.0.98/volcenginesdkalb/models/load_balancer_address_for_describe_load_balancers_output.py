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


class LoadBalancerAddressForDescribeLoadBalancersOutput(object):
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
        'eip': 'EipForDescribeLoadBalancersOutput',
        'eip_address': 'str',
        'eip_id': 'str',
        'eni_address': 'str',
        'eni_id': 'str',
        'eni_ipv6_address': 'str',
        'ipv6_eip': 'Ipv6EipForDescribeLoadBalancersOutput',
        'ipv6_eip_id': 'str'
    }

    attribute_map = {
        'eip': 'Eip',
        'eip_address': 'EipAddress',
        'eip_id': 'EipId',
        'eni_address': 'EniAddress',
        'eni_id': 'EniId',
        'eni_ipv6_address': 'EniIpv6Address',
        'ipv6_eip': 'Ipv6Eip',
        'ipv6_eip_id': 'Ipv6EipId'
    }

    def __init__(self, eip=None, eip_address=None, eip_id=None, eni_address=None, eni_id=None, eni_ipv6_address=None, ipv6_eip=None, ipv6_eip_id=None, _configuration=None):  # noqa: E501
        """LoadBalancerAddressForDescribeLoadBalancersOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._eip = None
        self._eip_address = None
        self._eip_id = None
        self._eni_address = None
        self._eni_id = None
        self._eni_ipv6_address = None
        self._ipv6_eip = None
        self._ipv6_eip_id = None
        self.discriminator = None

        if eip is not None:
            self.eip = eip
        if eip_address is not None:
            self.eip_address = eip_address
        if eip_id is not None:
            self.eip_id = eip_id
        if eni_address is not None:
            self.eni_address = eni_address
        if eni_id is not None:
            self.eni_id = eni_id
        if eni_ipv6_address is not None:
            self.eni_ipv6_address = eni_ipv6_address
        if ipv6_eip is not None:
            self.ipv6_eip = ipv6_eip
        if ipv6_eip_id is not None:
            self.ipv6_eip_id = ipv6_eip_id

    @property
    def eip(self):
        """Gets the eip of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501


        :return: The eip of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501
        :rtype: EipForDescribeLoadBalancersOutput
        """
        return self._eip

    @eip.setter
    def eip(self, eip):
        """Sets the eip of this LoadBalancerAddressForDescribeLoadBalancersOutput.


        :param eip: The eip of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501
        :type: EipForDescribeLoadBalancersOutput
        """

        self._eip = eip

    @property
    def eip_address(self):
        """Gets the eip_address of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501


        :return: The eip_address of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501
        :rtype: str
        """
        return self._eip_address

    @eip_address.setter
    def eip_address(self, eip_address):
        """Sets the eip_address of this LoadBalancerAddressForDescribeLoadBalancersOutput.


        :param eip_address: The eip_address of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501
        :type: str
        """

        self._eip_address = eip_address

    @property
    def eip_id(self):
        """Gets the eip_id of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501


        :return: The eip_id of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501
        :rtype: str
        """
        return self._eip_id

    @eip_id.setter
    def eip_id(self, eip_id):
        """Sets the eip_id of this LoadBalancerAddressForDescribeLoadBalancersOutput.


        :param eip_id: The eip_id of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501
        :type: str
        """

        self._eip_id = eip_id

    @property
    def eni_address(self):
        """Gets the eni_address of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501


        :return: The eni_address of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501
        :rtype: str
        """
        return self._eni_address

    @eni_address.setter
    def eni_address(self, eni_address):
        """Sets the eni_address of this LoadBalancerAddressForDescribeLoadBalancersOutput.


        :param eni_address: The eni_address of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501
        :type: str
        """

        self._eni_address = eni_address

    @property
    def eni_id(self):
        """Gets the eni_id of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501


        :return: The eni_id of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501
        :rtype: str
        """
        return self._eni_id

    @eni_id.setter
    def eni_id(self, eni_id):
        """Sets the eni_id of this LoadBalancerAddressForDescribeLoadBalancersOutput.


        :param eni_id: The eni_id of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501
        :type: str
        """

        self._eni_id = eni_id

    @property
    def eni_ipv6_address(self):
        """Gets the eni_ipv6_address of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501


        :return: The eni_ipv6_address of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501
        :rtype: str
        """
        return self._eni_ipv6_address

    @eni_ipv6_address.setter
    def eni_ipv6_address(self, eni_ipv6_address):
        """Sets the eni_ipv6_address of this LoadBalancerAddressForDescribeLoadBalancersOutput.


        :param eni_ipv6_address: The eni_ipv6_address of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501
        :type: str
        """

        self._eni_ipv6_address = eni_ipv6_address

    @property
    def ipv6_eip(self):
        """Gets the ipv6_eip of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501


        :return: The ipv6_eip of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501
        :rtype: Ipv6EipForDescribeLoadBalancersOutput
        """
        return self._ipv6_eip

    @ipv6_eip.setter
    def ipv6_eip(self, ipv6_eip):
        """Sets the ipv6_eip of this LoadBalancerAddressForDescribeLoadBalancersOutput.


        :param ipv6_eip: The ipv6_eip of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501
        :type: Ipv6EipForDescribeLoadBalancersOutput
        """

        self._ipv6_eip = ipv6_eip

    @property
    def ipv6_eip_id(self):
        """Gets the ipv6_eip_id of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501


        :return: The ipv6_eip_id of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501
        :rtype: str
        """
        return self._ipv6_eip_id

    @ipv6_eip_id.setter
    def ipv6_eip_id(self, ipv6_eip_id):
        """Sets the ipv6_eip_id of this LoadBalancerAddressForDescribeLoadBalancersOutput.


        :param ipv6_eip_id: The ipv6_eip_id of this LoadBalancerAddressForDescribeLoadBalancersOutput.  # noqa: E501
        :type: str
        """

        self._ipv6_eip_id = ipv6_eip_id

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
        if issubclass(LoadBalancerAddressForDescribeLoadBalancersOutput, dict):
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
        if not isinstance(other, LoadBalancerAddressForDescribeLoadBalancersOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, LoadBalancerAddressForDescribeLoadBalancersOutput):
            return True

        return self.to_dict() != other.to_dict()
