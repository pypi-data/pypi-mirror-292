# coding: utf-8

"""
    waf

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class CreateBlockRuleRequest(object):
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
        'accurate': 'AccurateForCreateBlockRuleInput',
        'action': 'str',
        'advanced': 'int',
        'client_ip': 'str',
        'description': 'str',
        'enable': 'int',
        'host': 'str',
        'ip_add_type': 'int',
        'ip_group_id': 'list[int]',
        'name': 'str',
        'url': 'str'
    }

    attribute_map = {
        'accurate': 'Accurate',
        'action': 'Action',
        'advanced': 'Advanced',
        'client_ip': 'ClientIp',
        'description': 'Description',
        'enable': 'Enable',
        'host': 'Host',
        'ip_add_type': 'IpAddType',
        'ip_group_id': 'IpGroupId',
        'name': 'Name',
        'url': 'Url'
    }

    def __init__(self, accurate=None, action=None, advanced=None, client_ip=None, description=None, enable=None, host=None, ip_add_type=None, ip_group_id=None, name=None, url=None, _configuration=None):  # noqa: E501
        """CreateBlockRuleRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._accurate = None
        self._action = None
        self._advanced = None
        self._client_ip = None
        self._description = None
        self._enable = None
        self._host = None
        self._ip_add_type = None
        self._ip_group_id = None
        self._name = None
        self._url = None
        self.discriminator = None

        if accurate is not None:
            self.accurate = accurate
        self.action = action
        self.advanced = advanced
        if client_ip is not None:
            self.client_ip = client_ip
        if description is not None:
            self.description = description
        if enable is not None:
            self.enable = enable
        self.host = host
        if ip_add_type is not None:
            self.ip_add_type = ip_add_type
        if ip_group_id is not None:
            self.ip_group_id = ip_group_id
        self.name = name
        self.url = url

    @property
    def accurate(self):
        """Gets the accurate of this CreateBlockRuleRequest.  # noqa: E501


        :return: The accurate of this CreateBlockRuleRequest.  # noqa: E501
        :rtype: AccurateForCreateBlockRuleInput
        """
        return self._accurate

    @accurate.setter
    def accurate(self, accurate):
        """Sets the accurate of this CreateBlockRuleRequest.


        :param accurate: The accurate of this CreateBlockRuleRequest.  # noqa: E501
        :type: AccurateForCreateBlockRuleInput
        """

        self._accurate = accurate

    @property
    def action(self):
        """Gets the action of this CreateBlockRuleRequest.  # noqa: E501


        :return: The action of this CreateBlockRuleRequest.  # noqa: E501
        :rtype: str
        """
        return self._action

    @action.setter
    def action(self, action):
        """Sets the action of this CreateBlockRuleRequest.


        :param action: The action of this CreateBlockRuleRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and action is None:
            raise ValueError("Invalid value for `action`, must not be `None`")  # noqa: E501
        allowed_values = ["observe", "block"]  # noqa: E501
        if (self._configuration.client_side_validation and
                action not in allowed_values):
            raise ValueError(
                "Invalid value for `action` ({0}), must be one of {1}"  # noqa: E501
                .format(action, allowed_values)
            )

        self._action = action

    @property
    def advanced(self):
        """Gets the advanced of this CreateBlockRuleRequest.  # noqa: E501


        :return: The advanced of this CreateBlockRuleRequest.  # noqa: E501
        :rtype: int
        """
        return self._advanced

    @advanced.setter
    def advanced(self, advanced):
        """Sets the advanced of this CreateBlockRuleRequest.


        :param advanced: The advanced of this CreateBlockRuleRequest.  # noqa: E501
        :type: int
        """
        if self._configuration.client_side_validation and advanced is None:
            raise ValueError("Invalid value for `advanced`, must not be `None`")  # noqa: E501

        self._advanced = advanced

    @property
    def client_ip(self):
        """Gets the client_ip of this CreateBlockRuleRequest.  # noqa: E501


        :return: The client_ip of this CreateBlockRuleRequest.  # noqa: E501
        :rtype: str
        """
        return self._client_ip

    @client_ip.setter
    def client_ip(self, client_ip):
        """Sets the client_ip of this CreateBlockRuleRequest.


        :param client_ip: The client_ip of this CreateBlockRuleRequest.  # noqa: E501
        :type: str
        """

        self._client_ip = client_ip

    @property
    def description(self):
        """Gets the description of this CreateBlockRuleRequest.  # noqa: E501


        :return: The description of this CreateBlockRuleRequest.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this CreateBlockRuleRequest.


        :param description: The description of this CreateBlockRuleRequest.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def enable(self):
        """Gets the enable of this CreateBlockRuleRequest.  # noqa: E501


        :return: The enable of this CreateBlockRuleRequest.  # noqa: E501
        :rtype: int
        """
        return self._enable

    @enable.setter
    def enable(self, enable):
        """Sets the enable of this CreateBlockRuleRequest.


        :param enable: The enable of this CreateBlockRuleRequest.  # noqa: E501
        :type: int
        """

        self._enable = enable

    @property
    def host(self):
        """Gets the host of this CreateBlockRuleRequest.  # noqa: E501


        :return: The host of this CreateBlockRuleRequest.  # noqa: E501
        :rtype: str
        """
        return self._host

    @host.setter
    def host(self, host):
        """Sets the host of this CreateBlockRuleRequest.


        :param host: The host of this CreateBlockRuleRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and host is None:
            raise ValueError("Invalid value for `host`, must not be `None`")  # noqa: E501

        self._host = host

    @property
    def ip_add_type(self):
        """Gets the ip_add_type of this CreateBlockRuleRequest.  # noqa: E501


        :return: The ip_add_type of this CreateBlockRuleRequest.  # noqa: E501
        :rtype: int
        """
        return self._ip_add_type

    @ip_add_type.setter
    def ip_add_type(self, ip_add_type):
        """Sets the ip_add_type of this CreateBlockRuleRequest.


        :param ip_add_type: The ip_add_type of this CreateBlockRuleRequest.  # noqa: E501
        :type: int
        """

        self._ip_add_type = ip_add_type

    @property
    def ip_group_id(self):
        """Gets the ip_group_id of this CreateBlockRuleRequest.  # noqa: E501


        :return: The ip_group_id of this CreateBlockRuleRequest.  # noqa: E501
        :rtype: list[int]
        """
        return self._ip_group_id

    @ip_group_id.setter
    def ip_group_id(self, ip_group_id):
        """Sets the ip_group_id of this CreateBlockRuleRequest.


        :param ip_group_id: The ip_group_id of this CreateBlockRuleRequest.  # noqa: E501
        :type: list[int]
        """

        self._ip_group_id = ip_group_id

    @property
    def name(self):
        """Gets the name of this CreateBlockRuleRequest.  # noqa: E501


        :return: The name of this CreateBlockRuleRequest.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this CreateBlockRuleRequest.


        :param name: The name of this CreateBlockRuleRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def url(self):
        """Gets the url of this CreateBlockRuleRequest.  # noqa: E501


        :return: The url of this CreateBlockRuleRequest.  # noqa: E501
        :rtype: str
        """
        return self._url

    @url.setter
    def url(self, url):
        """Sets the url of this CreateBlockRuleRequest.


        :param url: The url of this CreateBlockRuleRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and url is None:
            raise ValueError("Invalid value for `url`, must not be `None`")  # noqa: E501

        self._url = url

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
        if issubclass(CreateBlockRuleRequest, dict):
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
        if not isinstance(other, CreateBlockRuleRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateBlockRuleRequest):
            return True

        return self.to_dict() != other.to_dict()
