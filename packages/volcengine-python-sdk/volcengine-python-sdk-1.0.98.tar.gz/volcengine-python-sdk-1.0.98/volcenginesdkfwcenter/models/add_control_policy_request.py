# coding: utf-8

"""
    fwcenter

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class AddControlPolicyRequest(object):
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
        'action': 'str',
        'description': 'str',
        'dest_port': 'str',
        'dest_port_type': 'str',
        'destination': 'str',
        'destination_type': 'str',
        'direction': 'str',
        'prio': 'int',
        'proto': 'str',
        'source': 'str',
        'source_type': 'str',
        'status': 'bool'
    }

    attribute_map = {
        'action': 'Action',
        'description': 'Description',
        'dest_port': 'DestPort',
        'dest_port_type': 'DestPortType',
        'destination': 'Destination',
        'destination_type': 'DestinationType',
        'direction': 'Direction',
        'prio': 'Prio',
        'proto': 'Proto',
        'source': 'Source',
        'source_type': 'SourceType',
        'status': 'Status'
    }

    def __init__(self, action=None, description=None, dest_port=None, dest_port_type=None, destination=None, destination_type=None, direction=None, prio=None, proto=None, source=None, source_type=None, status=None, _configuration=None):  # noqa: E501
        """AddControlPolicyRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._action = None
        self._description = None
        self._dest_port = None
        self._dest_port_type = None
        self._destination = None
        self._destination_type = None
        self._direction = None
        self._prio = None
        self._proto = None
        self._source = None
        self._source_type = None
        self._status = None
        self.discriminator = None

        self.action = action
        if description is not None:
            self.description = description
        if dest_port is not None:
            self.dest_port = dest_port
        if dest_port_type is not None:
            self.dest_port_type = dest_port_type
        self.destination = destination
        self.destination_type = destination_type
        self.direction = direction
        if prio is not None:
            self.prio = prio
        self.proto = proto
        self.source = source
        self.source_type = source_type
        if status is not None:
            self.status = status

    @property
    def action(self):
        """Gets the action of this AddControlPolicyRequest.  # noqa: E501


        :return: The action of this AddControlPolicyRequest.  # noqa: E501
        :rtype: str
        """
        return self._action

    @action.setter
    def action(self, action):
        """Sets the action of this AddControlPolicyRequest.


        :param action: The action of this AddControlPolicyRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and action is None:
            raise ValueError("Invalid value for `action`, must not be `None`")  # noqa: E501

        self._action = action

    @property
    def description(self):
        """Gets the description of this AddControlPolicyRequest.  # noqa: E501


        :return: The description of this AddControlPolicyRequest.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this AddControlPolicyRequest.


        :param description: The description of this AddControlPolicyRequest.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def dest_port(self):
        """Gets the dest_port of this AddControlPolicyRequest.  # noqa: E501


        :return: The dest_port of this AddControlPolicyRequest.  # noqa: E501
        :rtype: str
        """
        return self._dest_port

    @dest_port.setter
    def dest_port(self, dest_port):
        """Sets the dest_port of this AddControlPolicyRequest.


        :param dest_port: The dest_port of this AddControlPolicyRequest.  # noqa: E501
        :type: str
        """

        self._dest_port = dest_port

    @property
    def dest_port_type(self):
        """Gets the dest_port_type of this AddControlPolicyRequest.  # noqa: E501


        :return: The dest_port_type of this AddControlPolicyRequest.  # noqa: E501
        :rtype: str
        """
        return self._dest_port_type

    @dest_port_type.setter
    def dest_port_type(self, dest_port_type):
        """Sets the dest_port_type of this AddControlPolicyRequest.


        :param dest_port_type: The dest_port_type of this AddControlPolicyRequest.  # noqa: E501
        :type: str
        """

        self._dest_port_type = dest_port_type

    @property
    def destination(self):
        """Gets the destination of this AddControlPolicyRequest.  # noqa: E501


        :return: The destination of this AddControlPolicyRequest.  # noqa: E501
        :rtype: str
        """
        return self._destination

    @destination.setter
    def destination(self, destination):
        """Sets the destination of this AddControlPolicyRequest.


        :param destination: The destination of this AddControlPolicyRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and destination is None:
            raise ValueError("Invalid value for `destination`, must not be `None`")  # noqa: E501

        self._destination = destination

    @property
    def destination_type(self):
        """Gets the destination_type of this AddControlPolicyRequest.  # noqa: E501


        :return: The destination_type of this AddControlPolicyRequest.  # noqa: E501
        :rtype: str
        """
        return self._destination_type

    @destination_type.setter
    def destination_type(self, destination_type):
        """Sets the destination_type of this AddControlPolicyRequest.


        :param destination_type: The destination_type of this AddControlPolicyRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and destination_type is None:
            raise ValueError("Invalid value for `destination_type`, must not be `None`")  # noqa: E501

        self._destination_type = destination_type

    @property
    def direction(self):
        """Gets the direction of this AddControlPolicyRequest.  # noqa: E501


        :return: The direction of this AddControlPolicyRequest.  # noqa: E501
        :rtype: str
        """
        return self._direction

    @direction.setter
    def direction(self, direction):
        """Sets the direction of this AddControlPolicyRequest.


        :param direction: The direction of this AddControlPolicyRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and direction is None:
            raise ValueError("Invalid value for `direction`, must not be `None`")  # noqa: E501

        self._direction = direction

    @property
    def prio(self):
        """Gets the prio of this AddControlPolicyRequest.  # noqa: E501


        :return: The prio of this AddControlPolicyRequest.  # noqa: E501
        :rtype: int
        """
        return self._prio

    @prio.setter
    def prio(self, prio):
        """Sets the prio of this AddControlPolicyRequest.


        :param prio: The prio of this AddControlPolicyRequest.  # noqa: E501
        :type: int
        """

        self._prio = prio

    @property
    def proto(self):
        """Gets the proto of this AddControlPolicyRequest.  # noqa: E501


        :return: The proto of this AddControlPolicyRequest.  # noqa: E501
        :rtype: str
        """
        return self._proto

    @proto.setter
    def proto(self, proto):
        """Sets the proto of this AddControlPolicyRequest.


        :param proto: The proto of this AddControlPolicyRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and proto is None:
            raise ValueError("Invalid value for `proto`, must not be `None`")  # noqa: E501

        self._proto = proto

    @property
    def source(self):
        """Gets the source of this AddControlPolicyRequest.  # noqa: E501


        :return: The source of this AddControlPolicyRequest.  # noqa: E501
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source):
        """Sets the source of this AddControlPolicyRequest.


        :param source: The source of this AddControlPolicyRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and source is None:
            raise ValueError("Invalid value for `source`, must not be `None`")  # noqa: E501

        self._source = source

    @property
    def source_type(self):
        """Gets the source_type of this AddControlPolicyRequest.  # noqa: E501


        :return: The source_type of this AddControlPolicyRequest.  # noqa: E501
        :rtype: str
        """
        return self._source_type

    @source_type.setter
    def source_type(self, source_type):
        """Sets the source_type of this AddControlPolicyRequest.


        :param source_type: The source_type of this AddControlPolicyRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and source_type is None:
            raise ValueError("Invalid value for `source_type`, must not be `None`")  # noqa: E501

        self._source_type = source_type

    @property
    def status(self):
        """Gets the status of this AddControlPolicyRequest.  # noqa: E501


        :return: The status of this AddControlPolicyRequest.  # noqa: E501
        :rtype: bool
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this AddControlPolicyRequest.


        :param status: The status of this AddControlPolicyRequest.  # noqa: E501
        :type: bool
        """

        self._status = status

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
        if issubclass(AddControlPolicyRequest, dict):
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
        if not isinstance(other, AddControlPolicyRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AddControlPolicyRequest):
            return True

        return self.to_dict() != other.to_dict()
