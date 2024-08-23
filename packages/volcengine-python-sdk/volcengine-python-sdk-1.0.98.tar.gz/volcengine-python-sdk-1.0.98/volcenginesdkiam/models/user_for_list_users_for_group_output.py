# coding: utf-8

"""
    iam

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class UserForListUsersForGroupOutput(object):
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
        'display_name': 'str',
        'join_date': 'str',
        'user_name': 'str'
    }

    attribute_map = {
        'description': 'Description',
        'display_name': 'DisplayName',
        'join_date': 'JoinDate',
        'user_name': 'UserName'
    }

    def __init__(self, description=None, display_name=None, join_date=None, user_name=None, _configuration=None):  # noqa: E501
        """UserForListUsersForGroupOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._description = None
        self._display_name = None
        self._join_date = None
        self._user_name = None
        self.discriminator = None

        if description is not None:
            self.description = description
        if display_name is not None:
            self.display_name = display_name
        if join_date is not None:
            self.join_date = join_date
        if user_name is not None:
            self.user_name = user_name

    @property
    def description(self):
        """Gets the description of this UserForListUsersForGroupOutput.  # noqa: E501


        :return: The description of this UserForListUsersForGroupOutput.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this UserForListUsersForGroupOutput.


        :param description: The description of this UserForListUsersForGroupOutput.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def display_name(self):
        """Gets the display_name of this UserForListUsersForGroupOutput.  # noqa: E501


        :return: The display_name of this UserForListUsersForGroupOutput.  # noqa: E501
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """Sets the display_name of this UserForListUsersForGroupOutput.


        :param display_name: The display_name of this UserForListUsersForGroupOutput.  # noqa: E501
        :type: str
        """

        self._display_name = display_name

    @property
    def join_date(self):
        """Gets the join_date of this UserForListUsersForGroupOutput.  # noqa: E501


        :return: The join_date of this UserForListUsersForGroupOutput.  # noqa: E501
        :rtype: str
        """
        return self._join_date

    @join_date.setter
    def join_date(self, join_date):
        """Sets the join_date of this UserForListUsersForGroupOutput.


        :param join_date: The join_date of this UserForListUsersForGroupOutput.  # noqa: E501
        :type: str
        """

        self._join_date = join_date

    @property
    def user_name(self):
        """Gets the user_name of this UserForListUsersForGroupOutput.  # noqa: E501


        :return: The user_name of this UserForListUsersForGroupOutput.  # noqa: E501
        :rtype: str
        """
        return self._user_name

    @user_name.setter
    def user_name(self, user_name):
        """Sets the user_name of this UserForListUsersForGroupOutput.


        :param user_name: The user_name of this UserForListUsersForGroupOutput.  # noqa: E501
        :type: str
        """

        self._user_name = user_name

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
        if issubclass(UserForListUsersForGroupOutput, dict):
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
        if not isinstance(other, UserForListUsersForGroupOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UserForListUsersForGroupOutput):
            return True

        return self.to_dict() != other.to_dict()
