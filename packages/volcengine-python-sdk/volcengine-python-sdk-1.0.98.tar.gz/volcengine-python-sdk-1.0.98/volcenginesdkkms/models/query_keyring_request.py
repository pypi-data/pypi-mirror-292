# coding: utf-8

"""
    kms

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class QueryKeyringRequest(object):
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
        'keyring_name': 'str'
    }

    attribute_map = {
        'keyring_name': 'KeyringName'
    }

    def __init__(self, keyring_name=None, _configuration=None):  # noqa: E501
        """QueryKeyringRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._keyring_name = None
        self.discriminator = None

        self.keyring_name = keyring_name

    @property
    def keyring_name(self):
        """Gets the keyring_name of this QueryKeyringRequest.  # noqa: E501


        :return: The keyring_name of this QueryKeyringRequest.  # noqa: E501
        :rtype: str
        """
        return self._keyring_name

    @keyring_name.setter
    def keyring_name(self, keyring_name):
        """Sets the keyring_name of this QueryKeyringRequest.


        :param keyring_name: The keyring_name of this QueryKeyringRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and keyring_name is None:
            raise ValueError("Invalid value for `keyring_name`, must not be `None`")  # noqa: E501
        if (self._configuration.client_side_validation and
                keyring_name is not None and len(keyring_name) > 31):
            raise ValueError("Invalid value for `keyring_name`, length must be less than or equal to `31`")  # noqa: E501
        if (self._configuration.client_side_validation and
                keyring_name is not None and len(keyring_name) < 2):
            raise ValueError("Invalid value for `keyring_name`, length must be greater than or equal to `2`")  # noqa: E501

        self._keyring_name = keyring_name

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
        if issubclass(QueryKeyringRequest, dict):
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
        if not isinstance(other, QueryKeyringRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, QueryKeyringRequest):
            return True

        return self.to_dict() != other.to_dict()
