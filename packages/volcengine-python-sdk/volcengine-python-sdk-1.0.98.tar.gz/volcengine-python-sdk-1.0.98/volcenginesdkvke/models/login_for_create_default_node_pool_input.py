# coding: utf-8

"""
    vke

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class LoginForCreateDefaultNodePoolInput(object):
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
        'password': 'str',
        'ssh_key_pair_name': 'str'
    }

    attribute_map = {
        'password': 'Password',
        'ssh_key_pair_name': 'SshKeyPairName'
    }

    def __init__(self, password=None, ssh_key_pair_name=None, _configuration=None):  # noqa: E501
        """LoginForCreateDefaultNodePoolInput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._password = None
        self._ssh_key_pair_name = None
        self.discriminator = None

        if password is not None:
            self.password = password
        if ssh_key_pair_name is not None:
            self.ssh_key_pair_name = ssh_key_pair_name

    @property
    def password(self):
        """Gets the password of this LoginForCreateDefaultNodePoolInput.  # noqa: E501


        :return: The password of this LoginForCreateDefaultNodePoolInput.  # noqa: E501
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """Sets the password of this LoginForCreateDefaultNodePoolInput.


        :param password: The password of this LoginForCreateDefaultNodePoolInput.  # noqa: E501
        :type: str
        """

        self._password = password

    @property
    def ssh_key_pair_name(self):
        """Gets the ssh_key_pair_name of this LoginForCreateDefaultNodePoolInput.  # noqa: E501


        :return: The ssh_key_pair_name of this LoginForCreateDefaultNodePoolInput.  # noqa: E501
        :rtype: str
        """
        return self._ssh_key_pair_name

    @ssh_key_pair_name.setter
    def ssh_key_pair_name(self, ssh_key_pair_name):
        """Sets the ssh_key_pair_name of this LoginForCreateDefaultNodePoolInput.


        :param ssh_key_pair_name: The ssh_key_pair_name of this LoginForCreateDefaultNodePoolInput.  # noqa: E501
        :type: str
        """

        self._ssh_key_pair_name = ssh_key_pair_name

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
        if issubclass(LoginForCreateDefaultNodePoolInput, dict):
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
        if not isinstance(other, LoginForCreateDefaultNodePoolInput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, LoginForCreateDefaultNodePoolInput):
            return True

        return self.to_dict() != other.to_dict()
