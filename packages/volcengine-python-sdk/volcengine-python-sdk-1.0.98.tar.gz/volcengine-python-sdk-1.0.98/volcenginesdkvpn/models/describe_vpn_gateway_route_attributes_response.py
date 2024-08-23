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


class DescribeVpnGatewayRouteAttributesResponse(object):
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
        'creation_time': 'str',
        'destination_cidr_block': 'str',
        'next_hop_id': 'str',
        'request_id': 'str',
        'status': 'str',
        'update_time': 'str',
        'vpn_gateway_id': 'str',
        'vpn_gateway_route_id': 'str'
    }

    attribute_map = {
        'creation_time': 'CreationTime',
        'destination_cidr_block': 'DestinationCidrBlock',
        'next_hop_id': 'NextHopId',
        'request_id': 'RequestId',
        'status': 'Status',
        'update_time': 'UpdateTime',
        'vpn_gateway_id': 'VpnGatewayId',
        'vpn_gateway_route_id': 'VpnGatewayRouteId'
    }

    def __init__(self, creation_time=None, destination_cidr_block=None, next_hop_id=None, request_id=None, status=None, update_time=None, vpn_gateway_id=None, vpn_gateway_route_id=None, _configuration=None):  # noqa: E501
        """DescribeVpnGatewayRouteAttributesResponse - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._creation_time = None
        self._destination_cidr_block = None
        self._next_hop_id = None
        self._request_id = None
        self._status = None
        self._update_time = None
        self._vpn_gateway_id = None
        self._vpn_gateway_route_id = None
        self.discriminator = None

        if creation_time is not None:
            self.creation_time = creation_time
        if destination_cidr_block is not None:
            self.destination_cidr_block = destination_cidr_block
        if next_hop_id is not None:
            self.next_hop_id = next_hop_id
        if request_id is not None:
            self.request_id = request_id
        if status is not None:
            self.status = status
        if update_time is not None:
            self.update_time = update_time
        if vpn_gateway_id is not None:
            self.vpn_gateway_id = vpn_gateway_id
        if vpn_gateway_route_id is not None:
            self.vpn_gateway_route_id = vpn_gateway_route_id

    @property
    def creation_time(self):
        """Gets the creation_time of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501


        :return: The creation_time of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._creation_time

    @creation_time.setter
    def creation_time(self, creation_time):
        """Sets the creation_time of this DescribeVpnGatewayRouteAttributesResponse.


        :param creation_time: The creation_time of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501
        :type: str
        """

        self._creation_time = creation_time

    @property
    def destination_cidr_block(self):
        """Gets the destination_cidr_block of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501


        :return: The destination_cidr_block of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._destination_cidr_block

    @destination_cidr_block.setter
    def destination_cidr_block(self, destination_cidr_block):
        """Sets the destination_cidr_block of this DescribeVpnGatewayRouteAttributesResponse.


        :param destination_cidr_block: The destination_cidr_block of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501
        :type: str
        """

        self._destination_cidr_block = destination_cidr_block

    @property
    def next_hop_id(self):
        """Gets the next_hop_id of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501


        :return: The next_hop_id of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._next_hop_id

    @next_hop_id.setter
    def next_hop_id(self, next_hop_id):
        """Sets the next_hop_id of this DescribeVpnGatewayRouteAttributesResponse.


        :param next_hop_id: The next_hop_id of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501
        :type: str
        """

        self._next_hop_id = next_hop_id

    @property
    def request_id(self):
        """Gets the request_id of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501


        :return: The request_id of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._request_id

    @request_id.setter
    def request_id(self, request_id):
        """Sets the request_id of this DescribeVpnGatewayRouteAttributesResponse.


        :param request_id: The request_id of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501
        :type: str
        """

        self._request_id = request_id

    @property
    def status(self):
        """Gets the status of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501


        :return: The status of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this DescribeVpnGatewayRouteAttributesResponse.


        :param status: The status of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def update_time(self):
        """Gets the update_time of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501


        :return: The update_time of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._update_time

    @update_time.setter
    def update_time(self, update_time):
        """Sets the update_time of this DescribeVpnGatewayRouteAttributesResponse.


        :param update_time: The update_time of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501
        :type: str
        """

        self._update_time = update_time

    @property
    def vpn_gateway_id(self):
        """Gets the vpn_gateway_id of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501


        :return: The vpn_gateway_id of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._vpn_gateway_id

    @vpn_gateway_id.setter
    def vpn_gateway_id(self, vpn_gateway_id):
        """Sets the vpn_gateway_id of this DescribeVpnGatewayRouteAttributesResponse.


        :param vpn_gateway_id: The vpn_gateway_id of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501
        :type: str
        """

        self._vpn_gateway_id = vpn_gateway_id

    @property
    def vpn_gateway_route_id(self):
        """Gets the vpn_gateway_route_id of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501


        :return: The vpn_gateway_route_id of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._vpn_gateway_route_id

    @vpn_gateway_route_id.setter
    def vpn_gateway_route_id(self, vpn_gateway_route_id):
        """Sets the vpn_gateway_route_id of this DescribeVpnGatewayRouteAttributesResponse.


        :param vpn_gateway_route_id: The vpn_gateway_route_id of this DescribeVpnGatewayRouteAttributesResponse.  # noqa: E501
        :type: str
        """

        self._vpn_gateway_route_id = vpn_gateway_route_id

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
        if issubclass(DescribeVpnGatewayRouteAttributesResponse, dict):
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
        if not isinstance(other, DescribeVpnGatewayRouteAttributesResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DescribeVpnGatewayRouteAttributesResponse):
            return True

        return self.to_dict() != other.to_dict()
