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


class DescribeSecurityGroupAttributesRequest(object):
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
        'cidr_ip': 'str',
        'direction': 'str',
        'prefix_list_id': 'str',
        'protocol': 'str',
        'security_group_id': 'str',
        'source_group_id': 'str'
    }

    attribute_map = {
        'cidr_ip': 'CidrIp',
        'direction': 'Direction',
        'prefix_list_id': 'PrefixListId',
        'protocol': 'Protocol',
        'security_group_id': 'SecurityGroupId',
        'source_group_id': 'SourceGroupId'
    }

    def __init__(self, cidr_ip=None, direction=None, prefix_list_id=None, protocol=None, security_group_id=None, source_group_id=None, _configuration=None):  # noqa: E501
        """DescribeSecurityGroupAttributesRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._cidr_ip = None
        self._direction = None
        self._prefix_list_id = None
        self._protocol = None
        self._security_group_id = None
        self._source_group_id = None
        self.discriminator = None

        if cidr_ip is not None:
            self.cidr_ip = cidr_ip
        if direction is not None:
            self.direction = direction
        if prefix_list_id is not None:
            self.prefix_list_id = prefix_list_id
        if protocol is not None:
            self.protocol = protocol
        self.security_group_id = security_group_id
        if source_group_id is not None:
            self.source_group_id = source_group_id

    @property
    def cidr_ip(self):
        """Gets the cidr_ip of this DescribeSecurityGroupAttributesRequest.  # noqa: E501


        :return: The cidr_ip of this DescribeSecurityGroupAttributesRequest.  # noqa: E501
        :rtype: str
        """
        return self._cidr_ip

    @cidr_ip.setter
    def cidr_ip(self, cidr_ip):
        """Sets the cidr_ip of this DescribeSecurityGroupAttributesRequest.


        :param cidr_ip: The cidr_ip of this DescribeSecurityGroupAttributesRequest.  # noqa: E501
        :type: str
        """

        self._cidr_ip = cidr_ip

    @property
    def direction(self):
        """Gets the direction of this DescribeSecurityGroupAttributesRequest.  # noqa: E501


        :return: The direction of this DescribeSecurityGroupAttributesRequest.  # noqa: E501
        :rtype: str
        """
        return self._direction

    @direction.setter
    def direction(self, direction):
        """Sets the direction of this DescribeSecurityGroupAttributesRequest.


        :param direction: The direction of this DescribeSecurityGroupAttributesRequest.  # noqa: E501
        :type: str
        """

        self._direction = direction

    @property
    def prefix_list_id(self):
        """Gets the prefix_list_id of this DescribeSecurityGroupAttributesRequest.  # noqa: E501


        :return: The prefix_list_id of this DescribeSecurityGroupAttributesRequest.  # noqa: E501
        :rtype: str
        """
        return self._prefix_list_id

    @prefix_list_id.setter
    def prefix_list_id(self, prefix_list_id):
        """Sets the prefix_list_id of this DescribeSecurityGroupAttributesRequest.


        :param prefix_list_id: The prefix_list_id of this DescribeSecurityGroupAttributesRequest.  # noqa: E501
        :type: str
        """

        self._prefix_list_id = prefix_list_id

    @property
    def protocol(self):
        """Gets the protocol of this DescribeSecurityGroupAttributesRequest.  # noqa: E501


        :return: The protocol of this DescribeSecurityGroupAttributesRequest.  # noqa: E501
        :rtype: str
        """
        return self._protocol

    @protocol.setter
    def protocol(self, protocol):
        """Sets the protocol of this DescribeSecurityGroupAttributesRequest.


        :param protocol: The protocol of this DescribeSecurityGroupAttributesRequest.  # noqa: E501
        :type: str
        """

        self._protocol = protocol

    @property
    def security_group_id(self):
        """Gets the security_group_id of this DescribeSecurityGroupAttributesRequest.  # noqa: E501


        :return: The security_group_id of this DescribeSecurityGroupAttributesRequest.  # noqa: E501
        :rtype: str
        """
        return self._security_group_id

    @security_group_id.setter
    def security_group_id(self, security_group_id):
        """Sets the security_group_id of this DescribeSecurityGroupAttributesRequest.


        :param security_group_id: The security_group_id of this DescribeSecurityGroupAttributesRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and security_group_id is None:
            raise ValueError("Invalid value for `security_group_id`, must not be `None`")  # noqa: E501

        self._security_group_id = security_group_id

    @property
    def source_group_id(self):
        """Gets the source_group_id of this DescribeSecurityGroupAttributesRequest.  # noqa: E501


        :return: The source_group_id of this DescribeSecurityGroupAttributesRequest.  # noqa: E501
        :rtype: str
        """
        return self._source_group_id

    @source_group_id.setter
    def source_group_id(self, source_group_id):
        """Sets the source_group_id of this DescribeSecurityGroupAttributesRequest.


        :param source_group_id: The source_group_id of this DescribeSecurityGroupAttributesRequest.  # noqa: E501
        :type: str
        """

        self._source_group_id = source_group_id

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
        if issubclass(DescribeSecurityGroupAttributesRequest, dict):
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
        if not isinstance(other, DescribeSecurityGroupAttributesRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DescribeSecurityGroupAttributesRequest):
            return True

        return self.to_dict() != other.to_dict()
