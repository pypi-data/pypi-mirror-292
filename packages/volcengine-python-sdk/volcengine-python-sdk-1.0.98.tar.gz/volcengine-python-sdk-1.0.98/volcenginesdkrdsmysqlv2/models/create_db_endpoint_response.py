# coding: utf-8

"""
    rds_mysql_v2

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class CreateDBEndpointResponse(object):
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
        'endpoint_id': 'str',
        'instance_id': 'str'
    }

    attribute_map = {
        'endpoint_id': 'EndpointId',
        'instance_id': 'InstanceId'
    }

    def __init__(self, endpoint_id=None, instance_id=None, _configuration=None):  # noqa: E501
        """CreateDBEndpointResponse - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._endpoint_id = None
        self._instance_id = None
        self.discriminator = None

        if endpoint_id is not None:
            self.endpoint_id = endpoint_id
        if instance_id is not None:
            self.instance_id = instance_id

    @property
    def endpoint_id(self):
        """Gets the endpoint_id of this CreateDBEndpointResponse.  # noqa: E501


        :return: The endpoint_id of this CreateDBEndpointResponse.  # noqa: E501
        :rtype: str
        """
        return self._endpoint_id

    @endpoint_id.setter
    def endpoint_id(self, endpoint_id):
        """Sets the endpoint_id of this CreateDBEndpointResponse.


        :param endpoint_id: The endpoint_id of this CreateDBEndpointResponse.  # noqa: E501
        :type: str
        """

        self._endpoint_id = endpoint_id

    @property
    def instance_id(self):
        """Gets the instance_id of this CreateDBEndpointResponse.  # noqa: E501


        :return: The instance_id of this CreateDBEndpointResponse.  # noqa: E501
        :rtype: str
        """
        return self._instance_id

    @instance_id.setter
    def instance_id(self, instance_id):
        """Sets the instance_id of this CreateDBEndpointResponse.


        :param instance_id: The instance_id of this CreateDBEndpointResponse.  # noqa: E501
        :type: str
        """

        self._instance_id = instance_id

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
        if issubclass(CreateDBEndpointResponse, dict):
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
        if not isinstance(other, CreateDBEndpointResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateDBEndpointResponse):
            return True

        return self.to_dict() != other.to_dict()
