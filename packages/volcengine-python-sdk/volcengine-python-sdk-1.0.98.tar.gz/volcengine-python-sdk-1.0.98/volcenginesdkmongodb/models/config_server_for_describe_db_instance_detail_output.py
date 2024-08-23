# coding: utf-8

"""
    mongodb

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class ConfigServerForDescribeDBInstanceDetailOutput(object):
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
        'config_server_node_id': 'str',
        'node_role': 'str',
        'node_status': 'str',
        'total_memory_gb': 'float',
        'totalv_cpu': 'float',
        'used_memory_gb': 'float',
        'usedv_cpu': 'float',
        'zone_id': 'str'
    }

    attribute_map = {
        'config_server_node_id': 'ConfigServerNodeId',
        'node_role': 'NodeRole',
        'node_status': 'NodeStatus',
        'total_memory_gb': 'TotalMemoryGB',
        'totalv_cpu': 'TotalvCPU',
        'used_memory_gb': 'UsedMemoryGB',
        'usedv_cpu': 'UsedvCPU',
        'zone_id': 'ZoneId'
    }

    def __init__(self, config_server_node_id=None, node_role=None, node_status=None, total_memory_gb=None, totalv_cpu=None, used_memory_gb=None, usedv_cpu=None, zone_id=None, _configuration=None):  # noqa: E501
        """ConfigServerForDescribeDBInstanceDetailOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._config_server_node_id = None
        self._node_role = None
        self._node_status = None
        self._total_memory_gb = None
        self._totalv_cpu = None
        self._used_memory_gb = None
        self._usedv_cpu = None
        self._zone_id = None
        self.discriminator = None

        if config_server_node_id is not None:
            self.config_server_node_id = config_server_node_id
        if node_role is not None:
            self.node_role = node_role
        if node_status is not None:
            self.node_status = node_status
        if total_memory_gb is not None:
            self.total_memory_gb = total_memory_gb
        if totalv_cpu is not None:
            self.totalv_cpu = totalv_cpu
        if used_memory_gb is not None:
            self.used_memory_gb = used_memory_gb
        if usedv_cpu is not None:
            self.usedv_cpu = usedv_cpu
        if zone_id is not None:
            self.zone_id = zone_id

    @property
    def config_server_node_id(self):
        """Gets the config_server_node_id of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501


        :return: The config_server_node_id of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501
        :rtype: str
        """
        return self._config_server_node_id

    @config_server_node_id.setter
    def config_server_node_id(self, config_server_node_id):
        """Sets the config_server_node_id of this ConfigServerForDescribeDBInstanceDetailOutput.


        :param config_server_node_id: The config_server_node_id of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501
        :type: str
        """

        self._config_server_node_id = config_server_node_id

    @property
    def node_role(self):
        """Gets the node_role of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501


        :return: The node_role of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501
        :rtype: str
        """
        return self._node_role

    @node_role.setter
    def node_role(self, node_role):
        """Sets the node_role of this ConfigServerForDescribeDBInstanceDetailOutput.


        :param node_role: The node_role of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501
        :type: str
        """

        self._node_role = node_role

    @property
    def node_status(self):
        """Gets the node_status of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501


        :return: The node_status of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501
        :rtype: str
        """
        return self._node_status

    @node_status.setter
    def node_status(self, node_status):
        """Sets the node_status of this ConfigServerForDescribeDBInstanceDetailOutput.


        :param node_status: The node_status of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501
        :type: str
        """

        self._node_status = node_status

    @property
    def total_memory_gb(self):
        """Gets the total_memory_gb of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501


        :return: The total_memory_gb of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501
        :rtype: float
        """
        return self._total_memory_gb

    @total_memory_gb.setter
    def total_memory_gb(self, total_memory_gb):
        """Sets the total_memory_gb of this ConfigServerForDescribeDBInstanceDetailOutput.


        :param total_memory_gb: The total_memory_gb of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501
        :type: float
        """

        self._total_memory_gb = total_memory_gb

    @property
    def totalv_cpu(self):
        """Gets the totalv_cpu of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501


        :return: The totalv_cpu of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501
        :rtype: float
        """
        return self._totalv_cpu

    @totalv_cpu.setter
    def totalv_cpu(self, totalv_cpu):
        """Sets the totalv_cpu of this ConfigServerForDescribeDBInstanceDetailOutput.


        :param totalv_cpu: The totalv_cpu of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501
        :type: float
        """

        self._totalv_cpu = totalv_cpu

    @property
    def used_memory_gb(self):
        """Gets the used_memory_gb of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501


        :return: The used_memory_gb of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501
        :rtype: float
        """
        return self._used_memory_gb

    @used_memory_gb.setter
    def used_memory_gb(self, used_memory_gb):
        """Sets the used_memory_gb of this ConfigServerForDescribeDBInstanceDetailOutput.


        :param used_memory_gb: The used_memory_gb of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501
        :type: float
        """

        self._used_memory_gb = used_memory_gb

    @property
    def usedv_cpu(self):
        """Gets the usedv_cpu of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501


        :return: The usedv_cpu of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501
        :rtype: float
        """
        return self._usedv_cpu

    @usedv_cpu.setter
    def usedv_cpu(self, usedv_cpu):
        """Sets the usedv_cpu of this ConfigServerForDescribeDBInstanceDetailOutput.


        :param usedv_cpu: The usedv_cpu of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501
        :type: float
        """

        self._usedv_cpu = usedv_cpu

    @property
    def zone_id(self):
        """Gets the zone_id of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501


        :return: The zone_id of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501
        :rtype: str
        """
        return self._zone_id

    @zone_id.setter
    def zone_id(self, zone_id):
        """Sets the zone_id of this ConfigServerForDescribeDBInstanceDetailOutput.


        :param zone_id: The zone_id of this ConfigServerForDescribeDBInstanceDetailOutput.  # noqa: E501
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
        if issubclass(ConfigServerForDescribeDBInstanceDetailOutput, dict):
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
        if not isinstance(other, ConfigServerForDescribeDBInstanceDetailOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ConfigServerForDescribeDBInstanceDetailOutput):
            return True

        return self.to_dict() != other.to_dict()
