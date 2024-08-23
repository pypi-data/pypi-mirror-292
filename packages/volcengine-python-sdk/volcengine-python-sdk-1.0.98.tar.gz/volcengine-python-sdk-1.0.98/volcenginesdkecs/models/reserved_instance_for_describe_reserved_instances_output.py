# coding: utf-8

"""
    ecs

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class ReservedInstanceForDescribeReservedInstancesOutput(object):
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
        'created_at': 'str',
        'expired_at': 'str',
        'hpc_cluster_id': 'str',
        'instance_count': 'int',
        'instance_type_id': 'str',
        'offering_type': 'str',
        'project_name': 'str',
        'region_id': 'str',
        'reserved_instance_id': 'str',
        'reserved_instance_name': 'str',
        'scope': 'str',
        'start_at': 'str',
        'status': 'str',
        'support_modify': 'str',
        'tags': 'list[TagForDescribeReservedInstancesOutput]',
        'zone_id': 'str'
    }

    attribute_map = {
        'created_at': 'CreatedAt',
        'expired_at': 'ExpiredAt',
        'hpc_cluster_id': 'HpcClusterId',
        'instance_count': 'InstanceCount',
        'instance_type_id': 'InstanceTypeId',
        'offering_type': 'OfferingType',
        'project_name': 'ProjectName',
        'region_id': 'RegionId',
        'reserved_instance_id': 'ReservedInstanceId',
        'reserved_instance_name': 'ReservedInstanceName',
        'scope': 'Scope',
        'start_at': 'StartAt',
        'status': 'Status',
        'support_modify': 'SupportModify',
        'tags': 'Tags',
        'zone_id': 'ZoneId'
    }

    def __init__(self, created_at=None, expired_at=None, hpc_cluster_id=None, instance_count=None, instance_type_id=None, offering_type=None, project_name=None, region_id=None, reserved_instance_id=None, reserved_instance_name=None, scope=None, start_at=None, status=None, support_modify=None, tags=None, zone_id=None, _configuration=None):  # noqa: E501
        """ReservedInstanceForDescribeReservedInstancesOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._created_at = None
        self._expired_at = None
        self._hpc_cluster_id = None
        self._instance_count = None
        self._instance_type_id = None
        self._offering_type = None
        self._project_name = None
        self._region_id = None
        self._reserved_instance_id = None
        self._reserved_instance_name = None
        self._scope = None
        self._start_at = None
        self._status = None
        self._support_modify = None
        self._tags = None
        self._zone_id = None
        self.discriminator = None

        if created_at is not None:
            self.created_at = created_at
        if expired_at is not None:
            self.expired_at = expired_at
        if hpc_cluster_id is not None:
            self.hpc_cluster_id = hpc_cluster_id
        if instance_count is not None:
            self.instance_count = instance_count
        if instance_type_id is not None:
            self.instance_type_id = instance_type_id
        if offering_type is not None:
            self.offering_type = offering_type
        if project_name is not None:
            self.project_name = project_name
        if region_id is not None:
            self.region_id = region_id
        if reserved_instance_id is not None:
            self.reserved_instance_id = reserved_instance_id
        if reserved_instance_name is not None:
            self.reserved_instance_name = reserved_instance_name
        if scope is not None:
            self.scope = scope
        if start_at is not None:
            self.start_at = start_at
        if status is not None:
            self.status = status
        if support_modify is not None:
            self.support_modify = support_modify
        if tags is not None:
            self.tags = tags
        if zone_id is not None:
            self.zone_id = zone_id

    @property
    def created_at(self):
        """Gets the created_at of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501


        :return: The created_at of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :rtype: str
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this ReservedInstanceForDescribeReservedInstancesOutput.


        :param created_at: The created_at of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :type: str
        """

        self._created_at = created_at

    @property
    def expired_at(self):
        """Gets the expired_at of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501


        :return: The expired_at of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :rtype: str
        """
        return self._expired_at

    @expired_at.setter
    def expired_at(self, expired_at):
        """Sets the expired_at of this ReservedInstanceForDescribeReservedInstancesOutput.


        :param expired_at: The expired_at of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :type: str
        """

        self._expired_at = expired_at

    @property
    def hpc_cluster_id(self):
        """Gets the hpc_cluster_id of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501


        :return: The hpc_cluster_id of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :rtype: str
        """
        return self._hpc_cluster_id

    @hpc_cluster_id.setter
    def hpc_cluster_id(self, hpc_cluster_id):
        """Sets the hpc_cluster_id of this ReservedInstanceForDescribeReservedInstancesOutput.


        :param hpc_cluster_id: The hpc_cluster_id of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :type: str
        """

        self._hpc_cluster_id = hpc_cluster_id

    @property
    def instance_count(self):
        """Gets the instance_count of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501


        :return: The instance_count of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :rtype: int
        """
        return self._instance_count

    @instance_count.setter
    def instance_count(self, instance_count):
        """Sets the instance_count of this ReservedInstanceForDescribeReservedInstancesOutput.


        :param instance_count: The instance_count of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :type: int
        """

        self._instance_count = instance_count

    @property
    def instance_type_id(self):
        """Gets the instance_type_id of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501


        :return: The instance_type_id of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :rtype: str
        """
        return self._instance_type_id

    @instance_type_id.setter
    def instance_type_id(self, instance_type_id):
        """Sets the instance_type_id of this ReservedInstanceForDescribeReservedInstancesOutput.


        :param instance_type_id: The instance_type_id of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :type: str
        """

        self._instance_type_id = instance_type_id

    @property
    def offering_type(self):
        """Gets the offering_type of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501


        :return: The offering_type of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :rtype: str
        """
        return self._offering_type

    @offering_type.setter
    def offering_type(self, offering_type):
        """Sets the offering_type of this ReservedInstanceForDescribeReservedInstancesOutput.


        :param offering_type: The offering_type of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :type: str
        """

        self._offering_type = offering_type

    @property
    def project_name(self):
        """Gets the project_name of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501


        :return: The project_name of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :rtype: str
        """
        return self._project_name

    @project_name.setter
    def project_name(self, project_name):
        """Sets the project_name of this ReservedInstanceForDescribeReservedInstancesOutput.


        :param project_name: The project_name of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :type: str
        """

        self._project_name = project_name

    @property
    def region_id(self):
        """Gets the region_id of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501


        :return: The region_id of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :rtype: str
        """
        return self._region_id

    @region_id.setter
    def region_id(self, region_id):
        """Sets the region_id of this ReservedInstanceForDescribeReservedInstancesOutput.


        :param region_id: The region_id of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :type: str
        """

        self._region_id = region_id

    @property
    def reserved_instance_id(self):
        """Gets the reserved_instance_id of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501


        :return: The reserved_instance_id of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :rtype: str
        """
        return self._reserved_instance_id

    @reserved_instance_id.setter
    def reserved_instance_id(self, reserved_instance_id):
        """Sets the reserved_instance_id of this ReservedInstanceForDescribeReservedInstancesOutput.


        :param reserved_instance_id: The reserved_instance_id of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :type: str
        """

        self._reserved_instance_id = reserved_instance_id

    @property
    def reserved_instance_name(self):
        """Gets the reserved_instance_name of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501


        :return: The reserved_instance_name of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :rtype: str
        """
        return self._reserved_instance_name

    @reserved_instance_name.setter
    def reserved_instance_name(self, reserved_instance_name):
        """Sets the reserved_instance_name of this ReservedInstanceForDescribeReservedInstancesOutput.


        :param reserved_instance_name: The reserved_instance_name of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :type: str
        """

        self._reserved_instance_name = reserved_instance_name

    @property
    def scope(self):
        """Gets the scope of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501


        :return: The scope of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :rtype: str
        """
        return self._scope

    @scope.setter
    def scope(self, scope):
        """Sets the scope of this ReservedInstanceForDescribeReservedInstancesOutput.


        :param scope: The scope of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :type: str
        """

        self._scope = scope

    @property
    def start_at(self):
        """Gets the start_at of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501


        :return: The start_at of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :rtype: str
        """
        return self._start_at

    @start_at.setter
    def start_at(self, start_at):
        """Sets the start_at of this ReservedInstanceForDescribeReservedInstancesOutput.


        :param start_at: The start_at of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :type: str
        """

        self._start_at = start_at

    @property
    def status(self):
        """Gets the status of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501


        :return: The status of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this ReservedInstanceForDescribeReservedInstancesOutput.


        :param status: The status of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def support_modify(self):
        """Gets the support_modify of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501


        :return: The support_modify of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :rtype: str
        """
        return self._support_modify

    @support_modify.setter
    def support_modify(self, support_modify):
        """Sets the support_modify of this ReservedInstanceForDescribeReservedInstancesOutput.


        :param support_modify: The support_modify of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :type: str
        """

        self._support_modify = support_modify

    @property
    def tags(self):
        """Gets the tags of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501


        :return: The tags of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :rtype: list[TagForDescribeReservedInstancesOutput]
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """Sets the tags of this ReservedInstanceForDescribeReservedInstancesOutput.


        :param tags: The tags of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :type: list[TagForDescribeReservedInstancesOutput]
        """

        self._tags = tags

    @property
    def zone_id(self):
        """Gets the zone_id of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501


        :return: The zone_id of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
        :rtype: str
        """
        return self._zone_id

    @zone_id.setter
    def zone_id(self, zone_id):
        """Sets the zone_id of this ReservedInstanceForDescribeReservedInstancesOutput.


        :param zone_id: The zone_id of this ReservedInstanceForDescribeReservedInstancesOutput.  # noqa: E501
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
        if issubclass(ReservedInstanceForDescribeReservedInstancesOutput, dict):
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
        if not isinstance(other, ReservedInstanceForDescribeReservedInstancesOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ReservedInstanceForDescribeReservedInstancesOutput):
            return True

        return self.to_dict() != other.to_dict()
