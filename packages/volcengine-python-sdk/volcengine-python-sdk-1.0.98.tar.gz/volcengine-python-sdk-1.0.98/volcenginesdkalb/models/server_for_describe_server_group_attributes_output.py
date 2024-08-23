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


class ServerForDescribeServerGroupAttributesOutput(object):
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
        'instance_id': 'str',
        'ip': 'str',
        'port': 'int',
        'remote_enabled': 'str',
        'server_id': 'str',
        'type': 'str',
        'weight': 'int'
    }

    attribute_map = {
        'description': 'Description',
        'instance_id': 'InstanceId',
        'ip': 'Ip',
        'port': 'Port',
        'remote_enabled': 'RemoteEnabled',
        'server_id': 'ServerId',
        'type': 'Type',
        'weight': 'Weight'
    }

    def __init__(self, description=None, instance_id=None, ip=None, port=None, remote_enabled=None, server_id=None, type=None, weight=None, _configuration=None):  # noqa: E501
        """ServerForDescribeServerGroupAttributesOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._description = None
        self._instance_id = None
        self._ip = None
        self._port = None
        self._remote_enabled = None
        self._server_id = None
        self._type = None
        self._weight = None
        self.discriminator = None

        if description is not None:
            self.description = description
        if instance_id is not None:
            self.instance_id = instance_id
        if ip is not None:
            self.ip = ip
        if port is not None:
            self.port = port
        if remote_enabled is not None:
            self.remote_enabled = remote_enabled
        if server_id is not None:
            self.server_id = server_id
        if type is not None:
            self.type = type
        if weight is not None:
            self.weight = weight

    @property
    def description(self):
        """Gets the description of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501


        :return: The description of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this ServerForDescribeServerGroupAttributesOutput.


        :param description: The description of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def instance_id(self):
        """Gets the instance_id of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501


        :return: The instance_id of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501
        :rtype: str
        """
        return self._instance_id

    @instance_id.setter
    def instance_id(self, instance_id):
        """Sets the instance_id of this ServerForDescribeServerGroupAttributesOutput.


        :param instance_id: The instance_id of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501
        :type: str
        """

        self._instance_id = instance_id

    @property
    def ip(self):
        """Gets the ip of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501


        :return: The ip of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501
        :rtype: str
        """
        return self._ip

    @ip.setter
    def ip(self, ip):
        """Sets the ip of this ServerForDescribeServerGroupAttributesOutput.


        :param ip: The ip of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501
        :type: str
        """

        self._ip = ip

    @property
    def port(self):
        """Gets the port of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501


        :return: The port of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501
        :rtype: int
        """
        return self._port

    @port.setter
    def port(self, port):
        """Sets the port of this ServerForDescribeServerGroupAttributesOutput.


        :param port: The port of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501
        :type: int
        """

        self._port = port

    @property
    def remote_enabled(self):
        """Gets the remote_enabled of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501


        :return: The remote_enabled of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501
        :rtype: str
        """
        return self._remote_enabled

    @remote_enabled.setter
    def remote_enabled(self, remote_enabled):
        """Sets the remote_enabled of this ServerForDescribeServerGroupAttributesOutput.


        :param remote_enabled: The remote_enabled of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501
        :type: str
        """

        self._remote_enabled = remote_enabled

    @property
    def server_id(self):
        """Gets the server_id of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501


        :return: The server_id of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501
        :rtype: str
        """
        return self._server_id

    @server_id.setter
    def server_id(self, server_id):
        """Sets the server_id of this ServerForDescribeServerGroupAttributesOutput.


        :param server_id: The server_id of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501
        :type: str
        """

        self._server_id = server_id

    @property
    def type(self):
        """Gets the type of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501


        :return: The type of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this ServerForDescribeServerGroupAttributesOutput.


        :param type: The type of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501
        :type: str
        """

        self._type = type

    @property
    def weight(self):
        """Gets the weight of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501


        :return: The weight of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501
        :rtype: int
        """
        return self._weight

    @weight.setter
    def weight(self, weight):
        """Sets the weight of this ServerForDescribeServerGroupAttributesOutput.


        :param weight: The weight of this ServerForDescribeServerGroupAttributesOutput.  # noqa: E501
        :type: int
        """

        self._weight = weight

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
        if issubclass(ServerForDescribeServerGroupAttributesOutput, dict):
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
        if not isinstance(other, ServerForDescribeServerGroupAttributesOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ServerForDescribeServerGroupAttributesOutput):
            return True

        return self.to_dict() != other.to_dict()
