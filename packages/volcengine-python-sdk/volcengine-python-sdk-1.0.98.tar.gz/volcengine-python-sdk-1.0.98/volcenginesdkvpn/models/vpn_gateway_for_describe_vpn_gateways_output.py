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


class VpnGatewayForDescribeVpnGatewaysOutput(object):
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
        'account_id': 'str',
        'bandwidth': 'int',
        'billing_type': 'int',
        'business_status': 'str',
        'connection_count': 'int',
        'creation_time': 'str',
        'deleted_time': 'str',
        'description': 'str',
        'expired_time': 'str',
        'ip_address': 'str',
        'lock_reason': 'str',
        'project_name': 'str',
        'route_count': 'int',
        'status': 'str',
        'subnet_id': 'str',
        'tags': 'list[TagForDescribeVpnGatewaysOutput]',
        'update_time': 'str',
        'vpc_id': 'str',
        'vpn_gateway_id': 'str',
        'vpn_gateway_name': 'str'
    }

    attribute_map = {
        'account_id': 'AccountId',
        'bandwidth': 'Bandwidth',
        'billing_type': 'BillingType',
        'business_status': 'BusinessStatus',
        'connection_count': 'ConnectionCount',
        'creation_time': 'CreationTime',
        'deleted_time': 'DeletedTime',
        'description': 'Description',
        'expired_time': 'ExpiredTime',
        'ip_address': 'IpAddress',
        'lock_reason': 'LockReason',
        'project_name': 'ProjectName',
        'route_count': 'RouteCount',
        'status': 'Status',
        'subnet_id': 'SubnetId',
        'tags': 'Tags',
        'update_time': 'UpdateTime',
        'vpc_id': 'VpcId',
        'vpn_gateway_id': 'VpnGatewayId',
        'vpn_gateway_name': 'VpnGatewayName'
    }

    def __init__(self, account_id=None, bandwidth=None, billing_type=None, business_status=None, connection_count=None, creation_time=None, deleted_time=None, description=None, expired_time=None, ip_address=None, lock_reason=None, project_name=None, route_count=None, status=None, subnet_id=None, tags=None, update_time=None, vpc_id=None, vpn_gateway_id=None, vpn_gateway_name=None, _configuration=None):  # noqa: E501
        """VpnGatewayForDescribeVpnGatewaysOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._account_id = None
        self._bandwidth = None
        self._billing_type = None
        self._business_status = None
        self._connection_count = None
        self._creation_time = None
        self._deleted_time = None
        self._description = None
        self._expired_time = None
        self._ip_address = None
        self._lock_reason = None
        self._project_name = None
        self._route_count = None
        self._status = None
        self._subnet_id = None
        self._tags = None
        self._update_time = None
        self._vpc_id = None
        self._vpn_gateway_id = None
        self._vpn_gateway_name = None
        self.discriminator = None

        if account_id is not None:
            self.account_id = account_id
        if bandwidth is not None:
            self.bandwidth = bandwidth
        if billing_type is not None:
            self.billing_type = billing_type
        if business_status is not None:
            self.business_status = business_status
        if connection_count is not None:
            self.connection_count = connection_count
        if creation_time is not None:
            self.creation_time = creation_time
        if deleted_time is not None:
            self.deleted_time = deleted_time
        if description is not None:
            self.description = description
        if expired_time is not None:
            self.expired_time = expired_time
        if ip_address is not None:
            self.ip_address = ip_address
        if lock_reason is not None:
            self.lock_reason = lock_reason
        if project_name is not None:
            self.project_name = project_name
        if route_count is not None:
            self.route_count = route_count
        if status is not None:
            self.status = status
        if subnet_id is not None:
            self.subnet_id = subnet_id
        if tags is not None:
            self.tags = tags
        if update_time is not None:
            self.update_time = update_time
        if vpc_id is not None:
            self.vpc_id = vpc_id
        if vpn_gateway_id is not None:
            self.vpn_gateway_id = vpn_gateway_id
        if vpn_gateway_name is not None:
            self.vpn_gateway_name = vpn_gateway_name

    @property
    def account_id(self):
        """Gets the account_id of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The account_id of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: str
        """
        return self._account_id

    @account_id.setter
    def account_id(self, account_id):
        """Sets the account_id of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param account_id: The account_id of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: str
        """

        self._account_id = account_id

    @property
    def bandwidth(self):
        """Gets the bandwidth of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The bandwidth of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: int
        """
        return self._bandwidth

    @bandwidth.setter
    def bandwidth(self, bandwidth):
        """Sets the bandwidth of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param bandwidth: The bandwidth of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: int
        """

        self._bandwidth = bandwidth

    @property
    def billing_type(self):
        """Gets the billing_type of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The billing_type of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: int
        """
        return self._billing_type

    @billing_type.setter
    def billing_type(self, billing_type):
        """Sets the billing_type of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param billing_type: The billing_type of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: int
        """

        self._billing_type = billing_type

    @property
    def business_status(self):
        """Gets the business_status of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The business_status of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: str
        """
        return self._business_status

    @business_status.setter
    def business_status(self, business_status):
        """Sets the business_status of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param business_status: The business_status of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: str
        """

        self._business_status = business_status

    @property
    def connection_count(self):
        """Gets the connection_count of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The connection_count of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: int
        """
        return self._connection_count

    @connection_count.setter
    def connection_count(self, connection_count):
        """Sets the connection_count of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param connection_count: The connection_count of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: int
        """

        self._connection_count = connection_count

    @property
    def creation_time(self):
        """Gets the creation_time of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The creation_time of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: str
        """
        return self._creation_time

    @creation_time.setter
    def creation_time(self, creation_time):
        """Sets the creation_time of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param creation_time: The creation_time of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: str
        """

        self._creation_time = creation_time

    @property
    def deleted_time(self):
        """Gets the deleted_time of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The deleted_time of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: str
        """
        return self._deleted_time

    @deleted_time.setter
    def deleted_time(self, deleted_time):
        """Sets the deleted_time of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param deleted_time: The deleted_time of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: str
        """

        self._deleted_time = deleted_time

    @property
    def description(self):
        """Gets the description of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The description of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param description: The description of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def expired_time(self):
        """Gets the expired_time of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The expired_time of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: str
        """
        return self._expired_time

    @expired_time.setter
    def expired_time(self, expired_time):
        """Sets the expired_time of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param expired_time: The expired_time of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: str
        """

        self._expired_time = expired_time

    @property
    def ip_address(self):
        """Gets the ip_address of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The ip_address of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: str
        """
        return self._ip_address

    @ip_address.setter
    def ip_address(self, ip_address):
        """Sets the ip_address of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param ip_address: The ip_address of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: str
        """

        self._ip_address = ip_address

    @property
    def lock_reason(self):
        """Gets the lock_reason of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The lock_reason of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: str
        """
        return self._lock_reason

    @lock_reason.setter
    def lock_reason(self, lock_reason):
        """Sets the lock_reason of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param lock_reason: The lock_reason of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: str
        """

        self._lock_reason = lock_reason

    @property
    def project_name(self):
        """Gets the project_name of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The project_name of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: str
        """
        return self._project_name

    @project_name.setter
    def project_name(self, project_name):
        """Sets the project_name of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param project_name: The project_name of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: str
        """

        self._project_name = project_name

    @property
    def route_count(self):
        """Gets the route_count of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The route_count of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: int
        """
        return self._route_count

    @route_count.setter
    def route_count(self, route_count):
        """Sets the route_count of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param route_count: The route_count of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: int
        """

        self._route_count = route_count

    @property
    def status(self):
        """Gets the status of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The status of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param status: The status of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def subnet_id(self):
        """Gets the subnet_id of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The subnet_id of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: str
        """
        return self._subnet_id

    @subnet_id.setter
    def subnet_id(self, subnet_id):
        """Sets the subnet_id of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param subnet_id: The subnet_id of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: str
        """

        self._subnet_id = subnet_id

    @property
    def tags(self):
        """Gets the tags of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The tags of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: list[TagForDescribeVpnGatewaysOutput]
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """Sets the tags of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param tags: The tags of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: list[TagForDescribeVpnGatewaysOutput]
        """

        self._tags = tags

    @property
    def update_time(self):
        """Gets the update_time of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The update_time of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: str
        """
        return self._update_time

    @update_time.setter
    def update_time(self, update_time):
        """Sets the update_time of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param update_time: The update_time of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: str
        """

        self._update_time = update_time

    @property
    def vpc_id(self):
        """Gets the vpc_id of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The vpc_id of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: str
        """
        return self._vpc_id

    @vpc_id.setter
    def vpc_id(self, vpc_id):
        """Sets the vpc_id of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param vpc_id: The vpc_id of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: str
        """

        self._vpc_id = vpc_id

    @property
    def vpn_gateway_id(self):
        """Gets the vpn_gateway_id of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The vpn_gateway_id of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: str
        """
        return self._vpn_gateway_id

    @vpn_gateway_id.setter
    def vpn_gateway_id(self, vpn_gateway_id):
        """Sets the vpn_gateway_id of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param vpn_gateway_id: The vpn_gateway_id of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: str
        """

        self._vpn_gateway_id = vpn_gateway_id

    @property
    def vpn_gateway_name(self):
        """Gets the vpn_gateway_name of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501


        :return: The vpn_gateway_name of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :rtype: str
        """
        return self._vpn_gateway_name

    @vpn_gateway_name.setter
    def vpn_gateway_name(self, vpn_gateway_name):
        """Sets the vpn_gateway_name of this VpnGatewayForDescribeVpnGatewaysOutput.


        :param vpn_gateway_name: The vpn_gateway_name of this VpnGatewayForDescribeVpnGatewaysOutput.  # noqa: E501
        :type: str
        """

        self._vpn_gateway_name = vpn_gateway_name

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
        if issubclass(VpnGatewayForDescribeVpnGatewaysOutput, dict):
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
        if not isinstance(other, VpnGatewayForDescribeVpnGatewaysOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, VpnGatewayForDescribeVpnGatewaysOutput):
            return True

        return self.to_dict() != other.to_dict()
