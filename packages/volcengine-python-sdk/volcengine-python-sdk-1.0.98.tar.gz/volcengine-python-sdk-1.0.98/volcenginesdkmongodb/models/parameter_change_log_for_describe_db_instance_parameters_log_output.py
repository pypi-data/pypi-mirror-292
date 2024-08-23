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


class ParameterChangeLogForDescribeDBInstanceParametersLogOutput(object):
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
        'modify_time': 'str',
        'new_parameter_value': 'str',
        'old_parameter_value': 'str',
        'parameter_name': 'str',
        'parameter_role': 'str',
        'parameter_status': 'str'
    }

    attribute_map = {
        'modify_time': 'ModifyTime',
        'new_parameter_value': 'NewParameterValue',
        'old_parameter_value': 'OldParameterValue',
        'parameter_name': 'ParameterName',
        'parameter_role': 'ParameterRole',
        'parameter_status': 'ParameterStatus'
    }

    def __init__(self, modify_time=None, new_parameter_value=None, old_parameter_value=None, parameter_name=None, parameter_role=None, parameter_status=None, _configuration=None):  # noqa: E501
        """ParameterChangeLogForDescribeDBInstanceParametersLogOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._modify_time = None
        self._new_parameter_value = None
        self._old_parameter_value = None
        self._parameter_name = None
        self._parameter_role = None
        self._parameter_status = None
        self.discriminator = None

        if modify_time is not None:
            self.modify_time = modify_time
        if new_parameter_value is not None:
            self.new_parameter_value = new_parameter_value
        if old_parameter_value is not None:
            self.old_parameter_value = old_parameter_value
        if parameter_name is not None:
            self.parameter_name = parameter_name
        if parameter_role is not None:
            self.parameter_role = parameter_role
        if parameter_status is not None:
            self.parameter_status = parameter_status

    @property
    def modify_time(self):
        """Gets the modify_time of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501


        :return: The modify_time of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501
        :rtype: str
        """
        return self._modify_time

    @modify_time.setter
    def modify_time(self, modify_time):
        """Sets the modify_time of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.


        :param modify_time: The modify_time of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501
        :type: str
        """

        self._modify_time = modify_time

    @property
    def new_parameter_value(self):
        """Gets the new_parameter_value of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501


        :return: The new_parameter_value of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501
        :rtype: str
        """
        return self._new_parameter_value

    @new_parameter_value.setter
    def new_parameter_value(self, new_parameter_value):
        """Sets the new_parameter_value of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.


        :param new_parameter_value: The new_parameter_value of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501
        :type: str
        """

        self._new_parameter_value = new_parameter_value

    @property
    def old_parameter_value(self):
        """Gets the old_parameter_value of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501


        :return: The old_parameter_value of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501
        :rtype: str
        """
        return self._old_parameter_value

    @old_parameter_value.setter
    def old_parameter_value(self, old_parameter_value):
        """Sets the old_parameter_value of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.


        :param old_parameter_value: The old_parameter_value of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501
        :type: str
        """

        self._old_parameter_value = old_parameter_value

    @property
    def parameter_name(self):
        """Gets the parameter_name of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501


        :return: The parameter_name of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501
        :rtype: str
        """
        return self._parameter_name

    @parameter_name.setter
    def parameter_name(self, parameter_name):
        """Sets the parameter_name of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.


        :param parameter_name: The parameter_name of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501
        :type: str
        """

        self._parameter_name = parameter_name

    @property
    def parameter_role(self):
        """Gets the parameter_role of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501


        :return: The parameter_role of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501
        :rtype: str
        """
        return self._parameter_role

    @parameter_role.setter
    def parameter_role(self, parameter_role):
        """Sets the parameter_role of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.


        :param parameter_role: The parameter_role of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501
        :type: str
        """

        self._parameter_role = parameter_role

    @property
    def parameter_status(self):
        """Gets the parameter_status of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501


        :return: The parameter_status of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501
        :rtype: str
        """
        return self._parameter_status

    @parameter_status.setter
    def parameter_status(self, parameter_status):
        """Sets the parameter_status of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.


        :param parameter_status: The parameter_status of this ParameterChangeLogForDescribeDBInstanceParametersLogOutput.  # noqa: E501
        :type: str
        """

        self._parameter_status = parameter_status

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
        if issubclass(ParameterChangeLogForDescribeDBInstanceParametersLogOutput, dict):
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
        if not isinstance(other, ParameterChangeLogForDescribeDBInstanceParametersLogOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ParameterChangeLogForDescribeDBInstanceParametersLogOutput):
            return True

        return self.to_dict() != other.to_dict()
