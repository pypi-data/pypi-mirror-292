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


class AuthResponseConfigForDescribeCdnConfigOutput(object):
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
        'cache_action': 'ConvertCacheActionForDescribeCdnConfigOutput',
        'response_action': 'ResponseActionForDescribeCdnConfigOutput',
        'status_code_action': 'StatusCodeActionForDescribeCdnConfigOutput',
        'time_out_action': 'TimeOutActionForDescribeCdnConfigOutput'
    }

    attribute_map = {
        'cache_action': 'CacheAction',
        'response_action': 'ResponseAction',
        'status_code_action': 'StatusCodeAction',
        'time_out_action': 'TimeOutAction'
    }

    def __init__(self, cache_action=None, response_action=None, status_code_action=None, time_out_action=None, _configuration=None):  # noqa: E501
        """AuthResponseConfigForDescribeCdnConfigOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._cache_action = None
        self._response_action = None
        self._status_code_action = None
        self._time_out_action = None
        self.discriminator = None

        if cache_action is not None:
            self.cache_action = cache_action
        if response_action is not None:
            self.response_action = response_action
        if status_code_action is not None:
            self.status_code_action = status_code_action
        if time_out_action is not None:
            self.time_out_action = time_out_action

    @property
    def cache_action(self):
        """Gets the cache_action of this AuthResponseConfigForDescribeCdnConfigOutput.  # noqa: E501


        :return: The cache_action of this AuthResponseConfigForDescribeCdnConfigOutput.  # noqa: E501
        :rtype: ConvertCacheActionForDescribeCdnConfigOutput
        """
        return self._cache_action

    @cache_action.setter
    def cache_action(self, cache_action):
        """Sets the cache_action of this AuthResponseConfigForDescribeCdnConfigOutput.


        :param cache_action: The cache_action of this AuthResponseConfigForDescribeCdnConfigOutput.  # noqa: E501
        :type: ConvertCacheActionForDescribeCdnConfigOutput
        """

        self._cache_action = cache_action

    @property
    def response_action(self):
        """Gets the response_action of this AuthResponseConfigForDescribeCdnConfigOutput.  # noqa: E501


        :return: The response_action of this AuthResponseConfigForDescribeCdnConfigOutput.  # noqa: E501
        :rtype: ResponseActionForDescribeCdnConfigOutput
        """
        return self._response_action

    @response_action.setter
    def response_action(self, response_action):
        """Sets the response_action of this AuthResponseConfigForDescribeCdnConfigOutput.


        :param response_action: The response_action of this AuthResponseConfigForDescribeCdnConfigOutput.  # noqa: E501
        :type: ResponseActionForDescribeCdnConfigOutput
        """

        self._response_action = response_action

    @property
    def status_code_action(self):
        """Gets the status_code_action of this AuthResponseConfigForDescribeCdnConfigOutput.  # noqa: E501


        :return: The status_code_action of this AuthResponseConfigForDescribeCdnConfigOutput.  # noqa: E501
        :rtype: StatusCodeActionForDescribeCdnConfigOutput
        """
        return self._status_code_action

    @status_code_action.setter
    def status_code_action(self, status_code_action):
        """Sets the status_code_action of this AuthResponseConfigForDescribeCdnConfigOutput.


        :param status_code_action: The status_code_action of this AuthResponseConfigForDescribeCdnConfigOutput.  # noqa: E501
        :type: StatusCodeActionForDescribeCdnConfigOutput
        """

        self._status_code_action = status_code_action

    @property
    def time_out_action(self):
        """Gets the time_out_action of this AuthResponseConfigForDescribeCdnConfigOutput.  # noqa: E501


        :return: The time_out_action of this AuthResponseConfigForDescribeCdnConfigOutput.  # noqa: E501
        :rtype: TimeOutActionForDescribeCdnConfigOutput
        """
        return self._time_out_action

    @time_out_action.setter
    def time_out_action(self, time_out_action):
        """Sets the time_out_action of this AuthResponseConfigForDescribeCdnConfigOutput.


        :param time_out_action: The time_out_action of this AuthResponseConfigForDescribeCdnConfigOutput.  # noqa: E501
        :type: TimeOutActionForDescribeCdnConfigOutput
        """

        self._time_out_action = time_out_action

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
        if issubclass(AuthResponseConfigForDescribeCdnConfigOutput, dict):
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
        if not isinstance(other, AuthResponseConfigForDescribeCdnConfigOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AuthResponseConfigForDescribeCdnConfigOutput):
            return True

        return self.to_dict() != other.to_dict()
