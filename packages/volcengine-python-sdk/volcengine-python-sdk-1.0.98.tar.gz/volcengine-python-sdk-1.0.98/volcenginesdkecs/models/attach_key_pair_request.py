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


class AttachKeyPairRequest(object):
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
        'client_token': 'str',
        'instance_ids': 'list[str]',
        'key_pair_id': 'str',
        'key_pair_name': 'str'
    }

    attribute_map = {
        'client_token': 'ClientToken',
        'instance_ids': 'InstanceIds',
        'key_pair_id': 'KeyPairId',
        'key_pair_name': 'KeyPairName'
    }

    def __init__(self, client_token=None, instance_ids=None, key_pair_id=None, key_pair_name=None, _configuration=None):  # noqa: E501
        """AttachKeyPairRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._client_token = None
        self._instance_ids = None
        self._key_pair_id = None
        self._key_pair_name = None
        self.discriminator = None

        if client_token is not None:
            self.client_token = client_token
        if instance_ids is not None:
            self.instance_ids = instance_ids
        if key_pair_id is not None:
            self.key_pair_id = key_pair_id
        if key_pair_name is not None:
            self.key_pair_name = key_pair_name

    @property
    def client_token(self):
        """Gets the client_token of this AttachKeyPairRequest.  # noqa: E501


        :return: The client_token of this AttachKeyPairRequest.  # noqa: E501
        :rtype: str
        """
        return self._client_token

    @client_token.setter
    def client_token(self, client_token):
        """Sets the client_token of this AttachKeyPairRequest.


        :param client_token: The client_token of this AttachKeyPairRequest.  # noqa: E501
        :type: str
        """

        self._client_token = client_token

    @property
    def instance_ids(self):
        """Gets the instance_ids of this AttachKeyPairRequest.  # noqa: E501


        :return: The instance_ids of this AttachKeyPairRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._instance_ids

    @instance_ids.setter
    def instance_ids(self, instance_ids):
        """Sets the instance_ids of this AttachKeyPairRequest.


        :param instance_ids: The instance_ids of this AttachKeyPairRequest.  # noqa: E501
        :type: list[str]
        """

        self._instance_ids = instance_ids

    @property
    def key_pair_id(self):
        """Gets the key_pair_id of this AttachKeyPairRequest.  # noqa: E501


        :return: The key_pair_id of this AttachKeyPairRequest.  # noqa: E501
        :rtype: str
        """
        return self._key_pair_id

    @key_pair_id.setter
    def key_pair_id(self, key_pair_id):
        """Sets the key_pair_id of this AttachKeyPairRequest.


        :param key_pair_id: The key_pair_id of this AttachKeyPairRequest.  # noqa: E501
        :type: str
        """

        self._key_pair_id = key_pair_id

    @property
    def key_pair_name(self):
        """Gets the key_pair_name of this AttachKeyPairRequest.  # noqa: E501


        :return: The key_pair_name of this AttachKeyPairRequest.  # noqa: E501
        :rtype: str
        """
        return self._key_pair_name

    @key_pair_name.setter
    def key_pair_name(self, key_pair_name):
        """Sets the key_pair_name of this AttachKeyPairRequest.


        :param key_pair_name: The key_pair_name of this AttachKeyPairRequest.  # noqa: E501
        :type: str
        """

        self._key_pair_name = key_pair_name

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
        if issubclass(AttachKeyPairRequest, dict):
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
        if not isinstance(other, AttachKeyPairRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AttachKeyPairRequest):
            return True

        return self.to_dict() != other.to_dict()
