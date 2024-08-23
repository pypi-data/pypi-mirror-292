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


class DescribeKeysRequest(object):
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
        'current_page': 'int',
        'keyring_name': 'str',
        'page_size': 'int'
    }

    attribute_map = {
        'current_page': 'CurrentPage',
        'keyring_name': 'KeyringName',
        'page_size': 'PageSize'
    }

    def __init__(self, current_page=None, keyring_name=None, page_size=None, _configuration=None):  # noqa: E501
        """DescribeKeysRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._current_page = None
        self._keyring_name = None
        self._page_size = None
        self.discriminator = None

        if current_page is not None:
            self.current_page = current_page
        self.keyring_name = keyring_name
        if page_size is not None:
            self.page_size = page_size

    @property
    def current_page(self):
        """Gets the current_page of this DescribeKeysRequest.  # noqa: E501


        :return: The current_page of this DescribeKeysRequest.  # noqa: E501
        :rtype: int
        """
        return self._current_page

    @current_page.setter
    def current_page(self, current_page):
        """Sets the current_page of this DescribeKeysRequest.


        :param current_page: The current_page of this DescribeKeysRequest.  # noqa: E501
        :type: int
        """
        if (self._configuration.client_side_validation and
                current_page is not None and current_page < 1):  # noqa: E501
            raise ValueError("Invalid value for `current_page`, must be a value greater than or equal to `1`")  # noqa: E501

        self._current_page = current_page

    @property
    def keyring_name(self):
        """Gets the keyring_name of this DescribeKeysRequest.  # noqa: E501


        :return: The keyring_name of this DescribeKeysRequest.  # noqa: E501
        :rtype: str
        """
        return self._keyring_name

    @keyring_name.setter
    def keyring_name(self, keyring_name):
        """Sets the keyring_name of this DescribeKeysRequest.


        :param keyring_name: The keyring_name of this DescribeKeysRequest.  # noqa: E501
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

    @property
    def page_size(self):
        """Gets the page_size of this DescribeKeysRequest.  # noqa: E501


        :return: The page_size of this DescribeKeysRequest.  # noqa: E501
        :rtype: int
        """
        return self._page_size

    @page_size.setter
    def page_size(self, page_size):
        """Sets the page_size of this DescribeKeysRequest.


        :param page_size: The page_size of this DescribeKeysRequest.  # noqa: E501
        :type: int
        """
        if (self._configuration.client_side_validation and
                page_size is not None and page_size > 100):  # noqa: E501
            raise ValueError("Invalid value for `page_size`, must be a value less than or equal to `100`")  # noqa: E501
        if (self._configuration.client_side_validation and
                page_size is not None and page_size < 1):  # noqa: E501
            raise ValueError("Invalid value for `page_size`, must be a value greater than or equal to `1`")  # noqa: E501

        self._page_size = page_size

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
        if issubclass(DescribeKeysRequest, dict):
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
        if not isinstance(other, DescribeKeysRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DescribeKeysRequest):
            return True

        return self.to_dict() != other.to_dict()
