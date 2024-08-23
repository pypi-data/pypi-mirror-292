# coding: utf-8

"""
    vedbm

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class MaintenanceWindowForDescribeDBInstanceDetailOutput(object):
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
        'day_kind': 'str',
        'day_of_month': 'list[int]',
        'day_of_week': 'list[str]',
        'maintenance_time': 'str'
    }

    attribute_map = {
        'day_kind': 'DayKind',
        'day_of_month': 'DayOfMonth',
        'day_of_week': 'DayOfWeek',
        'maintenance_time': 'MaintenanceTime'
    }

    def __init__(self, day_kind=None, day_of_month=None, day_of_week=None, maintenance_time=None, _configuration=None):  # noqa: E501
        """MaintenanceWindowForDescribeDBInstanceDetailOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._day_kind = None
        self._day_of_month = None
        self._day_of_week = None
        self._maintenance_time = None
        self.discriminator = None

        if day_kind is not None:
            self.day_kind = day_kind
        if day_of_month is not None:
            self.day_of_month = day_of_month
        if day_of_week is not None:
            self.day_of_week = day_of_week
        if maintenance_time is not None:
            self.maintenance_time = maintenance_time

    @property
    def day_kind(self):
        """Gets the day_kind of this MaintenanceWindowForDescribeDBInstanceDetailOutput.  # noqa: E501


        :return: The day_kind of this MaintenanceWindowForDescribeDBInstanceDetailOutput.  # noqa: E501
        :rtype: str
        """
        return self._day_kind

    @day_kind.setter
    def day_kind(self, day_kind):
        """Sets the day_kind of this MaintenanceWindowForDescribeDBInstanceDetailOutput.


        :param day_kind: The day_kind of this MaintenanceWindowForDescribeDBInstanceDetailOutput.  # noqa: E501
        :type: str
        """

        self._day_kind = day_kind

    @property
    def day_of_month(self):
        """Gets the day_of_month of this MaintenanceWindowForDescribeDBInstanceDetailOutput.  # noqa: E501


        :return: The day_of_month of this MaintenanceWindowForDescribeDBInstanceDetailOutput.  # noqa: E501
        :rtype: list[int]
        """
        return self._day_of_month

    @day_of_month.setter
    def day_of_month(self, day_of_month):
        """Sets the day_of_month of this MaintenanceWindowForDescribeDBInstanceDetailOutput.


        :param day_of_month: The day_of_month of this MaintenanceWindowForDescribeDBInstanceDetailOutput.  # noqa: E501
        :type: list[int]
        """

        self._day_of_month = day_of_month

    @property
    def day_of_week(self):
        """Gets the day_of_week of this MaintenanceWindowForDescribeDBInstanceDetailOutput.  # noqa: E501


        :return: The day_of_week of this MaintenanceWindowForDescribeDBInstanceDetailOutput.  # noqa: E501
        :rtype: list[str]
        """
        return self._day_of_week

    @day_of_week.setter
    def day_of_week(self, day_of_week):
        """Sets the day_of_week of this MaintenanceWindowForDescribeDBInstanceDetailOutput.


        :param day_of_week: The day_of_week of this MaintenanceWindowForDescribeDBInstanceDetailOutput.  # noqa: E501
        :type: list[str]
        """

        self._day_of_week = day_of_week

    @property
    def maintenance_time(self):
        """Gets the maintenance_time of this MaintenanceWindowForDescribeDBInstanceDetailOutput.  # noqa: E501


        :return: The maintenance_time of this MaintenanceWindowForDescribeDBInstanceDetailOutput.  # noqa: E501
        :rtype: str
        """
        return self._maintenance_time

    @maintenance_time.setter
    def maintenance_time(self, maintenance_time):
        """Sets the maintenance_time of this MaintenanceWindowForDescribeDBInstanceDetailOutput.


        :param maintenance_time: The maintenance_time of this MaintenanceWindowForDescribeDBInstanceDetailOutput.  # noqa: E501
        :type: str
        """

        self._maintenance_time = maintenance_time

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
        if issubclass(MaintenanceWindowForDescribeDBInstanceDetailOutput, dict):
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
        if not isinstance(other, MaintenanceWindowForDescribeDBInstanceDetailOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MaintenanceWindowForDescribeDBInstanceDetailOutput):
            return True

        return self.to_dict() != other.to_dict()
