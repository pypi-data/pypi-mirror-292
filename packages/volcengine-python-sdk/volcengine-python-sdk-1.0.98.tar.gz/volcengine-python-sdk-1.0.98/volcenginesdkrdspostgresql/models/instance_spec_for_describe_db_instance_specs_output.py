# coding: utf-8

"""
    rds_postgresql

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class InstanceSpecForDescribeDBInstanceSpecsOutput(object):
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
        'connection': 'int',
        'db_engine_version': 'str',
        'memory': 'int',
        'region_id': 'str',
        'spec_code': 'str',
        'spec_status': 'str',
        'vcpu': 'int',
        'zone_id': 'str'
    }

    attribute_map = {
        'connection': 'Connection',
        'db_engine_version': 'DBEngineVersion',
        'memory': 'Memory',
        'region_id': 'RegionId',
        'spec_code': 'SpecCode',
        'spec_status': 'SpecStatus',
        'vcpu': 'VCPU',
        'zone_id': 'ZoneId'
    }

    def __init__(self, connection=None, db_engine_version=None, memory=None, region_id=None, spec_code=None, spec_status=None, vcpu=None, zone_id=None, _configuration=None):  # noqa: E501
        """InstanceSpecForDescribeDBInstanceSpecsOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._connection = None
        self._db_engine_version = None
        self._memory = None
        self._region_id = None
        self._spec_code = None
        self._spec_status = None
        self._vcpu = None
        self._zone_id = None
        self.discriminator = None

        if connection is not None:
            self.connection = connection
        if db_engine_version is not None:
            self.db_engine_version = db_engine_version
        if memory is not None:
            self.memory = memory
        if region_id is not None:
            self.region_id = region_id
        if spec_code is not None:
            self.spec_code = spec_code
        if spec_status is not None:
            self.spec_status = spec_status
        if vcpu is not None:
            self.vcpu = vcpu
        if zone_id is not None:
            self.zone_id = zone_id

    @property
    def connection(self):
        """Gets the connection of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501


        :return: The connection of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501
        :rtype: int
        """
        return self._connection

    @connection.setter
    def connection(self, connection):
        """Sets the connection of this InstanceSpecForDescribeDBInstanceSpecsOutput.


        :param connection: The connection of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501
        :type: int
        """

        self._connection = connection

    @property
    def db_engine_version(self):
        """Gets the db_engine_version of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501


        :return: The db_engine_version of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501
        :rtype: str
        """
        return self._db_engine_version

    @db_engine_version.setter
    def db_engine_version(self, db_engine_version):
        """Sets the db_engine_version of this InstanceSpecForDescribeDBInstanceSpecsOutput.


        :param db_engine_version: The db_engine_version of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501
        :type: str
        """

        self._db_engine_version = db_engine_version

    @property
    def memory(self):
        """Gets the memory of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501


        :return: The memory of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501
        :rtype: int
        """
        return self._memory

    @memory.setter
    def memory(self, memory):
        """Sets the memory of this InstanceSpecForDescribeDBInstanceSpecsOutput.


        :param memory: The memory of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501
        :type: int
        """

        self._memory = memory

    @property
    def region_id(self):
        """Gets the region_id of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501


        :return: The region_id of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501
        :rtype: str
        """
        return self._region_id

    @region_id.setter
    def region_id(self, region_id):
        """Sets the region_id of this InstanceSpecForDescribeDBInstanceSpecsOutput.


        :param region_id: The region_id of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501
        :type: str
        """

        self._region_id = region_id

    @property
    def spec_code(self):
        """Gets the spec_code of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501


        :return: The spec_code of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501
        :rtype: str
        """
        return self._spec_code

    @spec_code.setter
    def spec_code(self, spec_code):
        """Sets the spec_code of this InstanceSpecForDescribeDBInstanceSpecsOutput.


        :param spec_code: The spec_code of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501
        :type: str
        """

        self._spec_code = spec_code

    @property
    def spec_status(self):
        """Gets the spec_status of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501


        :return: The spec_status of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501
        :rtype: str
        """
        return self._spec_status

    @spec_status.setter
    def spec_status(self, spec_status):
        """Sets the spec_status of this InstanceSpecForDescribeDBInstanceSpecsOutput.


        :param spec_status: The spec_status of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501
        :type: str
        """

        self._spec_status = spec_status

    @property
    def vcpu(self):
        """Gets the vcpu of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501


        :return: The vcpu of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501
        :rtype: int
        """
        return self._vcpu

    @vcpu.setter
    def vcpu(self, vcpu):
        """Sets the vcpu of this InstanceSpecForDescribeDBInstanceSpecsOutput.


        :param vcpu: The vcpu of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501
        :type: int
        """

        self._vcpu = vcpu

    @property
    def zone_id(self):
        """Gets the zone_id of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501


        :return: The zone_id of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501
        :rtype: str
        """
        return self._zone_id

    @zone_id.setter
    def zone_id(self, zone_id):
        """Sets the zone_id of this InstanceSpecForDescribeDBInstanceSpecsOutput.


        :param zone_id: The zone_id of this InstanceSpecForDescribeDBInstanceSpecsOutput.  # noqa: E501
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
        if issubclass(InstanceSpecForDescribeDBInstanceSpecsOutput, dict):
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
        if not isinstance(other, InstanceSpecForDescribeDBInstanceSpecsOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, InstanceSpecForDescribeDBInstanceSpecsOutput):
            return True

        return self.to_dict() != other.to_dict()
