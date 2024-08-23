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


class CreateVpnConnectionRequest(object):
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
        'attach_type': 'str',
        'client_token': 'str',
        'customer_gateway_id': 'str',
        'description': 'str',
        'dpd_action': 'str',
        'ike_config': 'str',
        'ipsec_config': 'str',
        'local_subnet': 'list[str]',
        'log_enabled': 'bool',
        'nat_traversal': 'bool',
        'negotiate_instantly': 'bool',
        'project_name': 'str',
        'remote_subnet': 'list[str]',
        'vpn_connection_name': 'str',
        'vpn_gateway_id': 'str'
    }

    attribute_map = {
        'attach_type': 'AttachType',
        'client_token': 'ClientToken',
        'customer_gateway_id': 'CustomerGatewayId',
        'description': 'Description',
        'dpd_action': 'DpdAction',
        'ike_config': 'IkeConfig',
        'ipsec_config': 'IpsecConfig',
        'local_subnet': 'LocalSubnet',
        'log_enabled': 'LogEnabled',
        'nat_traversal': 'NatTraversal',
        'negotiate_instantly': 'NegotiateInstantly',
        'project_name': 'ProjectName',
        'remote_subnet': 'RemoteSubnet',
        'vpn_connection_name': 'VpnConnectionName',
        'vpn_gateway_id': 'VpnGatewayId'
    }

    def __init__(self, attach_type=None, client_token=None, customer_gateway_id=None, description=None, dpd_action=None, ike_config=None, ipsec_config=None, local_subnet=None, log_enabled=None, nat_traversal=None, negotiate_instantly=None, project_name=None, remote_subnet=None, vpn_connection_name=None, vpn_gateway_id=None, _configuration=None):  # noqa: E501
        """CreateVpnConnectionRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._attach_type = None
        self._client_token = None
        self._customer_gateway_id = None
        self._description = None
        self._dpd_action = None
        self._ike_config = None
        self._ipsec_config = None
        self._local_subnet = None
        self._log_enabled = None
        self._nat_traversal = None
        self._negotiate_instantly = None
        self._project_name = None
        self._remote_subnet = None
        self._vpn_connection_name = None
        self._vpn_gateway_id = None
        self.discriminator = None

        if attach_type is not None:
            self.attach_type = attach_type
        if client_token is not None:
            self.client_token = client_token
        self.customer_gateway_id = customer_gateway_id
        if description is not None:
            self.description = description
        if dpd_action is not None:
            self.dpd_action = dpd_action
        if ike_config is not None:
            self.ike_config = ike_config
        if ipsec_config is not None:
            self.ipsec_config = ipsec_config
        if local_subnet is not None:
            self.local_subnet = local_subnet
        if log_enabled is not None:
            self.log_enabled = log_enabled
        if nat_traversal is not None:
            self.nat_traversal = nat_traversal
        if negotiate_instantly is not None:
            self.negotiate_instantly = negotiate_instantly
        if project_name is not None:
            self.project_name = project_name
        if remote_subnet is not None:
            self.remote_subnet = remote_subnet
        if vpn_connection_name is not None:
            self.vpn_connection_name = vpn_connection_name
        self.vpn_gateway_id = vpn_gateway_id

    @property
    def attach_type(self):
        """Gets the attach_type of this CreateVpnConnectionRequest.  # noqa: E501


        :return: The attach_type of this CreateVpnConnectionRequest.  # noqa: E501
        :rtype: str
        """
        return self._attach_type

    @attach_type.setter
    def attach_type(self, attach_type):
        """Sets the attach_type of this CreateVpnConnectionRequest.


        :param attach_type: The attach_type of this CreateVpnConnectionRequest.  # noqa: E501
        :type: str
        """
        allowed_values = ["VpnGateway", "TransitRouter"]  # noqa: E501
        if (self._configuration.client_side_validation and
                attach_type not in allowed_values):
            raise ValueError(
                "Invalid value for `attach_type` ({0}), must be one of {1}"  # noqa: E501
                .format(attach_type, allowed_values)
            )

        self._attach_type = attach_type

    @property
    def client_token(self):
        """Gets the client_token of this CreateVpnConnectionRequest.  # noqa: E501


        :return: The client_token of this CreateVpnConnectionRequest.  # noqa: E501
        :rtype: str
        """
        return self._client_token

    @client_token.setter
    def client_token(self, client_token):
        """Sets the client_token of this CreateVpnConnectionRequest.


        :param client_token: The client_token of this CreateVpnConnectionRequest.  # noqa: E501
        :type: str
        """

        self._client_token = client_token

    @property
    def customer_gateway_id(self):
        """Gets the customer_gateway_id of this CreateVpnConnectionRequest.  # noqa: E501


        :return: The customer_gateway_id of this CreateVpnConnectionRequest.  # noqa: E501
        :rtype: str
        """
        return self._customer_gateway_id

    @customer_gateway_id.setter
    def customer_gateway_id(self, customer_gateway_id):
        """Sets the customer_gateway_id of this CreateVpnConnectionRequest.


        :param customer_gateway_id: The customer_gateway_id of this CreateVpnConnectionRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and customer_gateway_id is None:
            raise ValueError("Invalid value for `customer_gateway_id`, must not be `None`")  # noqa: E501

        self._customer_gateway_id = customer_gateway_id

    @property
    def description(self):
        """Gets the description of this CreateVpnConnectionRequest.  # noqa: E501


        :return: The description of this CreateVpnConnectionRequest.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this CreateVpnConnectionRequest.


        :param description: The description of this CreateVpnConnectionRequest.  # noqa: E501
        :type: str
        """
        if (self._configuration.client_side_validation and
                description is not None and len(description) > 255):
            raise ValueError("Invalid value for `description`, length must be less than or equal to `255`")  # noqa: E501
        if (self._configuration.client_side_validation and
                description is not None and len(description) < 1):
            raise ValueError("Invalid value for `description`, length must be greater than or equal to `1`")  # noqa: E501

        self._description = description

    @property
    def dpd_action(self):
        """Gets the dpd_action of this CreateVpnConnectionRequest.  # noqa: E501


        :return: The dpd_action of this CreateVpnConnectionRequest.  # noqa: E501
        :rtype: str
        """
        return self._dpd_action

    @dpd_action.setter
    def dpd_action(self, dpd_action):
        """Sets the dpd_action of this CreateVpnConnectionRequest.


        :param dpd_action: The dpd_action of this CreateVpnConnectionRequest.  # noqa: E501
        :type: str
        """
        allowed_values = ["none", "clear", "hold", "restart"]  # noqa: E501
        if (self._configuration.client_side_validation and
                dpd_action not in allowed_values):
            raise ValueError(
                "Invalid value for `dpd_action` ({0}), must be one of {1}"  # noqa: E501
                .format(dpd_action, allowed_values)
            )

        self._dpd_action = dpd_action

    @property
    def ike_config(self):
        """Gets the ike_config of this CreateVpnConnectionRequest.  # noqa: E501


        :return: The ike_config of this CreateVpnConnectionRequest.  # noqa: E501
        :rtype: str
        """
        return self._ike_config

    @ike_config.setter
    def ike_config(self, ike_config):
        """Sets the ike_config of this CreateVpnConnectionRequest.


        :param ike_config: The ike_config of this CreateVpnConnectionRequest.  # noqa: E501
        :type: str
        """

        self._ike_config = ike_config

    @property
    def ipsec_config(self):
        """Gets the ipsec_config of this CreateVpnConnectionRequest.  # noqa: E501


        :return: The ipsec_config of this CreateVpnConnectionRequest.  # noqa: E501
        :rtype: str
        """
        return self._ipsec_config

    @ipsec_config.setter
    def ipsec_config(self, ipsec_config):
        """Sets the ipsec_config of this CreateVpnConnectionRequest.


        :param ipsec_config: The ipsec_config of this CreateVpnConnectionRequest.  # noqa: E501
        :type: str
        """

        self._ipsec_config = ipsec_config

    @property
    def local_subnet(self):
        """Gets the local_subnet of this CreateVpnConnectionRequest.  # noqa: E501


        :return: The local_subnet of this CreateVpnConnectionRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._local_subnet

    @local_subnet.setter
    def local_subnet(self, local_subnet):
        """Sets the local_subnet of this CreateVpnConnectionRequest.


        :param local_subnet: The local_subnet of this CreateVpnConnectionRequest.  # noqa: E501
        :type: list[str]
        """

        self._local_subnet = local_subnet

    @property
    def log_enabled(self):
        """Gets the log_enabled of this CreateVpnConnectionRequest.  # noqa: E501


        :return: The log_enabled of this CreateVpnConnectionRequest.  # noqa: E501
        :rtype: bool
        """
        return self._log_enabled

    @log_enabled.setter
    def log_enabled(self, log_enabled):
        """Sets the log_enabled of this CreateVpnConnectionRequest.


        :param log_enabled: The log_enabled of this CreateVpnConnectionRequest.  # noqa: E501
        :type: bool
        """

        self._log_enabled = log_enabled

    @property
    def nat_traversal(self):
        """Gets the nat_traversal of this CreateVpnConnectionRequest.  # noqa: E501


        :return: The nat_traversal of this CreateVpnConnectionRequest.  # noqa: E501
        :rtype: bool
        """
        return self._nat_traversal

    @nat_traversal.setter
    def nat_traversal(self, nat_traversal):
        """Sets the nat_traversal of this CreateVpnConnectionRequest.


        :param nat_traversal: The nat_traversal of this CreateVpnConnectionRequest.  # noqa: E501
        :type: bool
        """

        self._nat_traversal = nat_traversal

    @property
    def negotiate_instantly(self):
        """Gets the negotiate_instantly of this CreateVpnConnectionRequest.  # noqa: E501


        :return: The negotiate_instantly of this CreateVpnConnectionRequest.  # noqa: E501
        :rtype: bool
        """
        return self._negotiate_instantly

    @negotiate_instantly.setter
    def negotiate_instantly(self, negotiate_instantly):
        """Sets the negotiate_instantly of this CreateVpnConnectionRequest.


        :param negotiate_instantly: The negotiate_instantly of this CreateVpnConnectionRequest.  # noqa: E501
        :type: bool
        """

        self._negotiate_instantly = negotiate_instantly

    @property
    def project_name(self):
        """Gets the project_name of this CreateVpnConnectionRequest.  # noqa: E501


        :return: The project_name of this CreateVpnConnectionRequest.  # noqa: E501
        :rtype: str
        """
        return self._project_name

    @project_name.setter
    def project_name(self, project_name):
        """Sets the project_name of this CreateVpnConnectionRequest.


        :param project_name: The project_name of this CreateVpnConnectionRequest.  # noqa: E501
        :type: str
        """

        self._project_name = project_name

    @property
    def remote_subnet(self):
        """Gets the remote_subnet of this CreateVpnConnectionRequest.  # noqa: E501


        :return: The remote_subnet of this CreateVpnConnectionRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._remote_subnet

    @remote_subnet.setter
    def remote_subnet(self, remote_subnet):
        """Sets the remote_subnet of this CreateVpnConnectionRequest.


        :param remote_subnet: The remote_subnet of this CreateVpnConnectionRequest.  # noqa: E501
        :type: list[str]
        """

        self._remote_subnet = remote_subnet

    @property
    def vpn_connection_name(self):
        """Gets the vpn_connection_name of this CreateVpnConnectionRequest.  # noqa: E501


        :return: The vpn_connection_name of this CreateVpnConnectionRequest.  # noqa: E501
        :rtype: str
        """
        return self._vpn_connection_name

    @vpn_connection_name.setter
    def vpn_connection_name(self, vpn_connection_name):
        """Sets the vpn_connection_name of this CreateVpnConnectionRequest.


        :param vpn_connection_name: The vpn_connection_name of this CreateVpnConnectionRequest.  # noqa: E501
        :type: str
        """
        if (self._configuration.client_side_validation and
                vpn_connection_name is not None and len(vpn_connection_name) > 128):
            raise ValueError("Invalid value for `vpn_connection_name`, length must be less than or equal to `128`")  # noqa: E501
        if (self._configuration.client_side_validation and
                vpn_connection_name is not None and len(vpn_connection_name) < 1):
            raise ValueError("Invalid value for `vpn_connection_name`, length must be greater than or equal to `1`")  # noqa: E501

        self._vpn_connection_name = vpn_connection_name

    @property
    def vpn_gateway_id(self):
        """Gets the vpn_gateway_id of this CreateVpnConnectionRequest.  # noqa: E501


        :return: The vpn_gateway_id of this CreateVpnConnectionRequest.  # noqa: E501
        :rtype: str
        """
        return self._vpn_gateway_id

    @vpn_gateway_id.setter
    def vpn_gateway_id(self, vpn_gateway_id):
        """Sets the vpn_gateway_id of this CreateVpnConnectionRequest.


        :param vpn_gateway_id: The vpn_gateway_id of this CreateVpnConnectionRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and vpn_gateway_id is None:
            raise ValueError("Invalid value for `vpn_gateway_id`, must not be `None`")  # noqa: E501

        self._vpn_gateway_id = vpn_gateway_id

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
        if issubclass(CreateVpnConnectionRequest, dict):
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
        if not isinstance(other, CreateVpnConnectionRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateVpnConnectionRequest):
            return True

        return self.to_dict() != other.to_dict()
