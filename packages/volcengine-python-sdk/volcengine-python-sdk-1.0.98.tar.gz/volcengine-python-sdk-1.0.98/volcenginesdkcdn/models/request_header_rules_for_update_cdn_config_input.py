# coding: utf-8

"""
    cdn

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class RequestHeaderRulesForUpdateCdnConfigInput(object):
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
        'request_header_components': 'RequestHeaderComponentsForUpdateCdnConfigInput',
        'request_header_instances': 'list[RequestHeaderInstanceForUpdateCdnConfigInput]',
        'request_host': 'str'
    }

    attribute_map = {
        'request_header_components': 'RequestHeaderComponents',
        'request_header_instances': 'RequestHeaderInstances',
        'request_host': 'RequestHost'
    }

    def __init__(self, request_header_components=None, request_header_instances=None, request_host=None, _configuration=None):  # noqa: E501
        """RequestHeaderRulesForUpdateCdnConfigInput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._request_header_components = None
        self._request_header_instances = None
        self._request_host = None
        self.discriminator = None

        if request_header_components is not None:
            self.request_header_components = request_header_components
        if request_header_instances is not None:
            self.request_header_instances = request_header_instances
        if request_host is not None:
            self.request_host = request_host

    @property
    def request_header_components(self):
        """Gets the request_header_components of this RequestHeaderRulesForUpdateCdnConfigInput.  # noqa: E501


        :return: The request_header_components of this RequestHeaderRulesForUpdateCdnConfigInput.  # noqa: E501
        :rtype: RequestHeaderComponentsForUpdateCdnConfigInput
        """
        return self._request_header_components

    @request_header_components.setter
    def request_header_components(self, request_header_components):
        """Sets the request_header_components of this RequestHeaderRulesForUpdateCdnConfigInput.


        :param request_header_components: The request_header_components of this RequestHeaderRulesForUpdateCdnConfigInput.  # noqa: E501
        :type: RequestHeaderComponentsForUpdateCdnConfigInput
        """

        self._request_header_components = request_header_components

    @property
    def request_header_instances(self):
        """Gets the request_header_instances of this RequestHeaderRulesForUpdateCdnConfigInput.  # noqa: E501


        :return: The request_header_instances of this RequestHeaderRulesForUpdateCdnConfigInput.  # noqa: E501
        :rtype: list[RequestHeaderInstanceForUpdateCdnConfigInput]
        """
        return self._request_header_instances

    @request_header_instances.setter
    def request_header_instances(self, request_header_instances):
        """Sets the request_header_instances of this RequestHeaderRulesForUpdateCdnConfigInput.


        :param request_header_instances: The request_header_instances of this RequestHeaderRulesForUpdateCdnConfigInput.  # noqa: E501
        :type: list[RequestHeaderInstanceForUpdateCdnConfigInput]
        """

        self._request_header_instances = request_header_instances

    @property
    def request_host(self):
        """Gets the request_host of this RequestHeaderRulesForUpdateCdnConfigInput.  # noqa: E501


        :return: The request_host of this RequestHeaderRulesForUpdateCdnConfigInput.  # noqa: E501
        :rtype: str
        """
        return self._request_host

    @request_host.setter
    def request_host(self, request_host):
        """Sets the request_host of this RequestHeaderRulesForUpdateCdnConfigInput.


        :param request_host: The request_host of this RequestHeaderRulesForUpdateCdnConfigInput.  # noqa: E501
        :type: str
        """

        self._request_host = request_host

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
        if issubclass(RequestHeaderRulesForUpdateCdnConfigInput, dict):
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
        if not isinstance(other, RequestHeaderRulesForUpdateCdnConfigInput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, RequestHeaderRulesForUpdateCdnConfigInput):
            return True

        return self.to_dict() != other.to_dict()
