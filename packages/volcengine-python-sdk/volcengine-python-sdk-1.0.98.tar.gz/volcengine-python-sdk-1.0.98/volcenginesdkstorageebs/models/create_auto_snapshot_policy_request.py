# coding: utf-8

"""
    storage_ebs

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class CreateAutoSnapshotPolicyRequest(object):
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
        'auto_snapshot_policy_name': 'str',
        'project_name': 'str',
        'repeat_days': 'int',
        'repeat_weekdays': 'list[str]',
        'retention_days': 'int',
        'time_points': 'list[str]'
    }

    attribute_map = {
        'auto_snapshot_policy_name': 'AutoSnapshotPolicyName',
        'project_name': 'ProjectName',
        'repeat_days': 'RepeatDays',
        'repeat_weekdays': 'RepeatWeekdays',
        'retention_days': 'RetentionDays',
        'time_points': 'TimePoints'
    }

    def __init__(self, auto_snapshot_policy_name=None, project_name=None, repeat_days=None, repeat_weekdays=None, retention_days=None, time_points=None, _configuration=None):  # noqa: E501
        """CreateAutoSnapshotPolicyRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._auto_snapshot_policy_name = None
        self._project_name = None
        self._repeat_days = None
        self._repeat_weekdays = None
        self._retention_days = None
        self._time_points = None
        self.discriminator = None

        self.auto_snapshot_policy_name = auto_snapshot_policy_name
        if project_name is not None:
            self.project_name = project_name
        if repeat_days is not None:
            self.repeat_days = repeat_days
        if repeat_weekdays is not None:
            self.repeat_weekdays = repeat_weekdays
        self.retention_days = retention_days
        if time_points is not None:
            self.time_points = time_points

    @property
    def auto_snapshot_policy_name(self):
        """Gets the auto_snapshot_policy_name of this CreateAutoSnapshotPolicyRequest.  # noqa: E501


        :return: The auto_snapshot_policy_name of this CreateAutoSnapshotPolicyRequest.  # noqa: E501
        :rtype: str
        """
        return self._auto_snapshot_policy_name

    @auto_snapshot_policy_name.setter
    def auto_snapshot_policy_name(self, auto_snapshot_policy_name):
        """Sets the auto_snapshot_policy_name of this CreateAutoSnapshotPolicyRequest.


        :param auto_snapshot_policy_name: The auto_snapshot_policy_name of this CreateAutoSnapshotPolicyRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and auto_snapshot_policy_name is None:
            raise ValueError("Invalid value for `auto_snapshot_policy_name`, must not be `None`")  # noqa: E501

        self._auto_snapshot_policy_name = auto_snapshot_policy_name

    @property
    def project_name(self):
        """Gets the project_name of this CreateAutoSnapshotPolicyRequest.  # noqa: E501


        :return: The project_name of this CreateAutoSnapshotPolicyRequest.  # noqa: E501
        :rtype: str
        """
        return self._project_name

    @project_name.setter
    def project_name(self, project_name):
        """Sets the project_name of this CreateAutoSnapshotPolicyRequest.


        :param project_name: The project_name of this CreateAutoSnapshotPolicyRequest.  # noqa: E501
        :type: str
        """

        self._project_name = project_name

    @property
    def repeat_days(self):
        """Gets the repeat_days of this CreateAutoSnapshotPolicyRequest.  # noqa: E501


        :return: The repeat_days of this CreateAutoSnapshotPolicyRequest.  # noqa: E501
        :rtype: int
        """
        return self._repeat_days

    @repeat_days.setter
    def repeat_days(self, repeat_days):
        """Sets the repeat_days of this CreateAutoSnapshotPolicyRequest.


        :param repeat_days: The repeat_days of this CreateAutoSnapshotPolicyRequest.  # noqa: E501
        :type: int
        """

        self._repeat_days = repeat_days

    @property
    def repeat_weekdays(self):
        """Gets the repeat_weekdays of this CreateAutoSnapshotPolicyRequest.  # noqa: E501


        :return: The repeat_weekdays of this CreateAutoSnapshotPolicyRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._repeat_weekdays

    @repeat_weekdays.setter
    def repeat_weekdays(self, repeat_weekdays):
        """Sets the repeat_weekdays of this CreateAutoSnapshotPolicyRequest.


        :param repeat_weekdays: The repeat_weekdays of this CreateAutoSnapshotPolicyRequest.  # noqa: E501
        :type: list[str]
        """

        self._repeat_weekdays = repeat_weekdays

    @property
    def retention_days(self):
        """Gets the retention_days of this CreateAutoSnapshotPolicyRequest.  # noqa: E501


        :return: The retention_days of this CreateAutoSnapshotPolicyRequest.  # noqa: E501
        :rtype: int
        """
        return self._retention_days

    @retention_days.setter
    def retention_days(self, retention_days):
        """Sets the retention_days of this CreateAutoSnapshotPolicyRequest.


        :param retention_days: The retention_days of this CreateAutoSnapshotPolicyRequest.  # noqa: E501
        :type: int
        """
        if self._configuration.client_side_validation and retention_days is None:
            raise ValueError("Invalid value for `retention_days`, must not be `None`")  # noqa: E501

        self._retention_days = retention_days

    @property
    def time_points(self):
        """Gets the time_points of this CreateAutoSnapshotPolicyRequest.  # noqa: E501


        :return: The time_points of this CreateAutoSnapshotPolicyRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._time_points

    @time_points.setter
    def time_points(self, time_points):
        """Sets the time_points of this CreateAutoSnapshotPolicyRequest.


        :param time_points: The time_points of this CreateAutoSnapshotPolicyRequest.  # noqa: E501
        :type: list[str]
        """

        self._time_points = time_points

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
        if issubclass(CreateAutoSnapshotPolicyRequest, dict):
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
        if not isinstance(other, CreateAutoSnapshotPolicyRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateAutoSnapshotPolicyRequest):
            return True

        return self.to_dict() != other.to_dict()
