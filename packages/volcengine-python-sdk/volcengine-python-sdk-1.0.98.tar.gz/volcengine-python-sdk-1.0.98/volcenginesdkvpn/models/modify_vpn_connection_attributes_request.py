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


class ModifyVpnConnectionAttributesRequest(object):
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
        'description': 'str',
        'dpd_action': 'str',
        'ike_config': 'str',
        'ipsec_config': 'str',
        'local_subnet': 'list[str]',
        'log_enabled': 'bool',
        'nat_traversal': 'bool',
        'negotiate_instantly': 'bool',
        'remote_subnet': 'list[str]',
        'vpn_connection_id': 'str',
        'vpn_connection_name': 'str'
    }

    attribute_map = {
        'description': 'Description',
        'dpd_action': 'DpdAction',
        'ike_config': 'IkeConfig',
        'ipsec_config': 'IpsecConfig',
        'local_subnet': 'LocalSubnet',
        'log_enabled': 'LogEnabled',
        'nat_traversal': 'NatTraversal',
        'negotiate_instantly': 'NegotiateInstantly',
        'remote_subnet': 'RemoteSubnet',
        'vpn_connection_id': 'VpnConnectionId',
        'vpn_connection_name': 'VpnConnectionName'
    }

    def __init__(self, description=None, dpd_action=None, ike_config=None, ipsec_config=None, local_subnet=None, log_enabled=None, nat_traversal=None, negotiate_instantly=None, remote_subnet=None, vpn_connection_id=None, vpn_connection_name=None, _configuration=None):  # noqa: E501
        """ModifyVpnConnectionAttributesRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._description = None
        self._dpd_action = None
        self._ike_config = None
        self._ipsec_config = None
        self._local_subnet = None
        self._log_enabled = None
        self._nat_traversal = None
        self._negotiate_instantly = None
        self._remote_subnet = None
        self._vpn_connection_id = None
        self._vpn_connection_name = None
        self.discriminator = None

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
        if remote_subnet is not None:
            self.remote_subnet = remote_subnet
        self.vpn_connection_id = vpn_connection_id
        if vpn_connection_name is not None:
            self.vpn_connection_name = vpn_connection_name

    @property
    def description(self):
        """Gets the description of this ModifyVpnConnectionAttributesRequest.  # noqa: E501


        :return: The description of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this ModifyVpnConnectionAttributesRequest.


        :param description: The description of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
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
        """Gets the dpd_action of this ModifyVpnConnectionAttributesRequest.  # noqa: E501


        :return: The dpd_action of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :rtype: str
        """
        return self._dpd_action

    @dpd_action.setter
    def dpd_action(self, dpd_action):
        """Sets the dpd_action of this ModifyVpnConnectionAttributesRequest.


        :param dpd_action: The dpd_action of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
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
        """Gets the ike_config of this ModifyVpnConnectionAttributesRequest.  # noqa: E501


        :return: The ike_config of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :rtype: str
        """
        return self._ike_config

    @ike_config.setter
    def ike_config(self, ike_config):
        """Sets the ike_config of this ModifyVpnConnectionAttributesRequest.


        :param ike_config: The ike_config of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :type: str
        """

        self._ike_config = ike_config

    @property
    def ipsec_config(self):
        """Gets the ipsec_config of this ModifyVpnConnectionAttributesRequest.  # noqa: E501


        :return: The ipsec_config of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :rtype: str
        """
        return self._ipsec_config

    @ipsec_config.setter
    def ipsec_config(self, ipsec_config):
        """Sets the ipsec_config of this ModifyVpnConnectionAttributesRequest.


        :param ipsec_config: The ipsec_config of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :type: str
        """

        self._ipsec_config = ipsec_config

    @property
    def local_subnet(self):
        """Gets the local_subnet of this ModifyVpnConnectionAttributesRequest.  # noqa: E501


        :return: The local_subnet of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._local_subnet

    @local_subnet.setter
    def local_subnet(self, local_subnet):
        """Sets the local_subnet of this ModifyVpnConnectionAttributesRequest.


        :param local_subnet: The local_subnet of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :type: list[str]
        """

        self._local_subnet = local_subnet

    @property
    def log_enabled(self):
        """Gets the log_enabled of this ModifyVpnConnectionAttributesRequest.  # noqa: E501


        :return: The log_enabled of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :rtype: bool
        """
        return self._log_enabled

    @log_enabled.setter
    def log_enabled(self, log_enabled):
        """Sets the log_enabled of this ModifyVpnConnectionAttributesRequest.


        :param log_enabled: The log_enabled of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :type: bool
        """

        self._log_enabled = log_enabled

    @property
    def nat_traversal(self):
        """Gets the nat_traversal of this ModifyVpnConnectionAttributesRequest.  # noqa: E501


        :return: The nat_traversal of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :rtype: bool
        """
        return self._nat_traversal

    @nat_traversal.setter
    def nat_traversal(self, nat_traversal):
        """Sets the nat_traversal of this ModifyVpnConnectionAttributesRequest.


        :param nat_traversal: The nat_traversal of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :type: bool
        """

        self._nat_traversal = nat_traversal

    @property
    def negotiate_instantly(self):
        """Gets the negotiate_instantly of this ModifyVpnConnectionAttributesRequest.  # noqa: E501


        :return: The negotiate_instantly of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :rtype: bool
        """
        return self._negotiate_instantly

    @negotiate_instantly.setter
    def negotiate_instantly(self, negotiate_instantly):
        """Sets the negotiate_instantly of this ModifyVpnConnectionAttributesRequest.


        :param negotiate_instantly: The negotiate_instantly of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :type: bool
        """

        self._negotiate_instantly = negotiate_instantly

    @property
    def remote_subnet(self):
        """Gets the remote_subnet of this ModifyVpnConnectionAttributesRequest.  # noqa: E501


        :return: The remote_subnet of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._remote_subnet

    @remote_subnet.setter
    def remote_subnet(self, remote_subnet):
        """Sets the remote_subnet of this ModifyVpnConnectionAttributesRequest.


        :param remote_subnet: The remote_subnet of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :type: list[str]
        """

        self._remote_subnet = remote_subnet

    @property
    def vpn_connection_id(self):
        """Gets the vpn_connection_id of this ModifyVpnConnectionAttributesRequest.  # noqa: E501


        :return: The vpn_connection_id of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :rtype: str
        """
        return self._vpn_connection_id

    @vpn_connection_id.setter
    def vpn_connection_id(self, vpn_connection_id):
        """Sets the vpn_connection_id of this ModifyVpnConnectionAttributesRequest.


        :param vpn_connection_id: The vpn_connection_id of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and vpn_connection_id is None:
            raise ValueError("Invalid value for `vpn_connection_id`, must not be `None`")  # noqa: E501

        self._vpn_connection_id = vpn_connection_id

    @property
    def vpn_connection_name(self):
        """Gets the vpn_connection_name of this ModifyVpnConnectionAttributesRequest.  # noqa: E501


        :return: The vpn_connection_name of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :rtype: str
        """
        return self._vpn_connection_name

    @vpn_connection_name.setter
    def vpn_connection_name(self, vpn_connection_name):
        """Sets the vpn_connection_name of this ModifyVpnConnectionAttributesRequest.


        :param vpn_connection_name: The vpn_connection_name of this ModifyVpnConnectionAttributesRequest.  # noqa: E501
        :type: str
        """
        if (self._configuration.client_side_validation and
                vpn_connection_name is not None and len(vpn_connection_name) > 128):
            raise ValueError("Invalid value for `vpn_connection_name`, length must be less than or equal to `128`")  # noqa: E501
        if (self._configuration.client_side_validation and
                vpn_connection_name is not None and len(vpn_connection_name) < 1):
            raise ValueError("Invalid value for `vpn_connection_name`, length must be greater than or equal to `1`")  # noqa: E501

        self._vpn_connection_name = vpn_connection_name

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
        if issubclass(ModifyVpnConnectionAttributesRequest, dict):
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
        if not isinstance(other, ModifyVpnConnectionAttributesRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ModifyVpnConnectionAttributesRequest):
            return True

        return self.to_dict() != other.to_dict()
