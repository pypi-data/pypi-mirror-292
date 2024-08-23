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


class ServerGroupForDescribeServerGroupsOutput(object):
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
        'create_time': 'str',
        'description': 'str',
        'health_check': 'HealthCheckForDescribeServerGroupsOutput',
        'listeners': 'list[str]',
        'project_name': 'str',
        'scheduler': 'str',
        'server_count': 'int',
        'server_group_id': 'str',
        'server_group_name': 'str',
        'server_group_type': 'str',
        'status': 'str',
        'sticky_session_config': 'StickySessionConfigForDescribeServerGroupsOutput',
        'update_time': 'str',
        'vpc_id': 'str'
    }

    attribute_map = {
        'create_time': 'CreateTime',
        'description': 'Description',
        'health_check': 'HealthCheck',
        'listeners': 'Listeners',
        'project_name': 'ProjectName',
        'scheduler': 'Scheduler',
        'server_count': 'ServerCount',
        'server_group_id': 'ServerGroupId',
        'server_group_name': 'ServerGroupName',
        'server_group_type': 'ServerGroupType',
        'status': 'Status',
        'sticky_session_config': 'StickySessionConfig',
        'update_time': 'UpdateTime',
        'vpc_id': 'VpcId'
    }

    def __init__(self, create_time=None, description=None, health_check=None, listeners=None, project_name=None, scheduler=None, server_count=None, server_group_id=None, server_group_name=None, server_group_type=None, status=None, sticky_session_config=None, update_time=None, vpc_id=None, _configuration=None):  # noqa: E501
        """ServerGroupForDescribeServerGroupsOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._create_time = None
        self._description = None
        self._health_check = None
        self._listeners = None
        self._project_name = None
        self._scheduler = None
        self._server_count = None
        self._server_group_id = None
        self._server_group_name = None
        self._server_group_type = None
        self._status = None
        self._sticky_session_config = None
        self._update_time = None
        self._vpc_id = None
        self.discriminator = None

        if create_time is not None:
            self.create_time = create_time
        if description is not None:
            self.description = description
        if health_check is not None:
            self.health_check = health_check
        if listeners is not None:
            self.listeners = listeners
        if project_name is not None:
            self.project_name = project_name
        if scheduler is not None:
            self.scheduler = scheduler
        if server_count is not None:
            self.server_count = server_count
        if server_group_id is not None:
            self.server_group_id = server_group_id
        if server_group_name is not None:
            self.server_group_name = server_group_name
        if server_group_type is not None:
            self.server_group_type = server_group_type
        if status is not None:
            self.status = status
        if sticky_session_config is not None:
            self.sticky_session_config = sticky_session_config
        if update_time is not None:
            self.update_time = update_time
        if vpc_id is not None:
            self.vpc_id = vpc_id

    @property
    def create_time(self):
        """Gets the create_time of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501


        :return: The create_time of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :rtype: str
        """
        return self._create_time

    @create_time.setter
    def create_time(self, create_time):
        """Sets the create_time of this ServerGroupForDescribeServerGroupsOutput.


        :param create_time: The create_time of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :type: str
        """

        self._create_time = create_time

    @property
    def description(self):
        """Gets the description of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501


        :return: The description of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this ServerGroupForDescribeServerGroupsOutput.


        :param description: The description of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def health_check(self):
        """Gets the health_check of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501


        :return: The health_check of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :rtype: HealthCheckForDescribeServerGroupsOutput
        """
        return self._health_check

    @health_check.setter
    def health_check(self, health_check):
        """Sets the health_check of this ServerGroupForDescribeServerGroupsOutput.


        :param health_check: The health_check of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :type: HealthCheckForDescribeServerGroupsOutput
        """

        self._health_check = health_check

    @property
    def listeners(self):
        """Gets the listeners of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501


        :return: The listeners of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :rtype: list[str]
        """
        return self._listeners

    @listeners.setter
    def listeners(self, listeners):
        """Sets the listeners of this ServerGroupForDescribeServerGroupsOutput.


        :param listeners: The listeners of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :type: list[str]
        """

        self._listeners = listeners

    @property
    def project_name(self):
        """Gets the project_name of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501


        :return: The project_name of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :rtype: str
        """
        return self._project_name

    @project_name.setter
    def project_name(self, project_name):
        """Sets the project_name of this ServerGroupForDescribeServerGroupsOutput.


        :param project_name: The project_name of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :type: str
        """

        self._project_name = project_name

    @property
    def scheduler(self):
        """Gets the scheduler of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501


        :return: The scheduler of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :rtype: str
        """
        return self._scheduler

    @scheduler.setter
    def scheduler(self, scheduler):
        """Sets the scheduler of this ServerGroupForDescribeServerGroupsOutput.


        :param scheduler: The scheduler of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :type: str
        """

        self._scheduler = scheduler

    @property
    def server_count(self):
        """Gets the server_count of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501


        :return: The server_count of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :rtype: int
        """
        return self._server_count

    @server_count.setter
    def server_count(self, server_count):
        """Sets the server_count of this ServerGroupForDescribeServerGroupsOutput.


        :param server_count: The server_count of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :type: int
        """

        self._server_count = server_count

    @property
    def server_group_id(self):
        """Gets the server_group_id of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501


        :return: The server_group_id of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :rtype: str
        """
        return self._server_group_id

    @server_group_id.setter
    def server_group_id(self, server_group_id):
        """Sets the server_group_id of this ServerGroupForDescribeServerGroupsOutput.


        :param server_group_id: The server_group_id of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :type: str
        """

        self._server_group_id = server_group_id

    @property
    def server_group_name(self):
        """Gets the server_group_name of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501


        :return: The server_group_name of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :rtype: str
        """
        return self._server_group_name

    @server_group_name.setter
    def server_group_name(self, server_group_name):
        """Sets the server_group_name of this ServerGroupForDescribeServerGroupsOutput.


        :param server_group_name: The server_group_name of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :type: str
        """

        self._server_group_name = server_group_name

    @property
    def server_group_type(self):
        """Gets the server_group_type of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501


        :return: The server_group_type of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :rtype: str
        """
        return self._server_group_type

    @server_group_type.setter
    def server_group_type(self, server_group_type):
        """Sets the server_group_type of this ServerGroupForDescribeServerGroupsOutput.


        :param server_group_type: The server_group_type of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :type: str
        """

        self._server_group_type = server_group_type

    @property
    def status(self):
        """Gets the status of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501


        :return: The status of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this ServerGroupForDescribeServerGroupsOutput.


        :param status: The status of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def sticky_session_config(self):
        """Gets the sticky_session_config of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501


        :return: The sticky_session_config of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :rtype: StickySessionConfigForDescribeServerGroupsOutput
        """
        return self._sticky_session_config

    @sticky_session_config.setter
    def sticky_session_config(self, sticky_session_config):
        """Sets the sticky_session_config of this ServerGroupForDescribeServerGroupsOutput.


        :param sticky_session_config: The sticky_session_config of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :type: StickySessionConfigForDescribeServerGroupsOutput
        """

        self._sticky_session_config = sticky_session_config

    @property
    def update_time(self):
        """Gets the update_time of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501


        :return: The update_time of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :rtype: str
        """
        return self._update_time

    @update_time.setter
    def update_time(self, update_time):
        """Sets the update_time of this ServerGroupForDescribeServerGroupsOutput.


        :param update_time: The update_time of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :type: str
        """

        self._update_time = update_time

    @property
    def vpc_id(self):
        """Gets the vpc_id of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501


        :return: The vpc_id of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :rtype: str
        """
        return self._vpc_id

    @vpc_id.setter
    def vpc_id(self, vpc_id):
        """Sets the vpc_id of this ServerGroupForDescribeServerGroupsOutput.


        :param vpc_id: The vpc_id of this ServerGroupForDescribeServerGroupsOutput.  # noqa: E501
        :type: str
        """

        self._vpc_id = vpc_id

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
        if issubclass(ServerGroupForDescribeServerGroupsOutput, dict):
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
        if not isinstance(other, ServerGroupForDescribeServerGroupsOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ServerGroupForDescribeServerGroupsOutput):
            return True

        return self.to_dict() != other.to_dict()
