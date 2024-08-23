# coding: utf-8

"""
    waf

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class UpdateAreaBlockRuleRequest(object):
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
        'action': 'str',
        'country': 'list[str]',
        'host': 'str',
        'sub_region': 'list[str]'
    }

    attribute_map = {
        'action': 'Action',
        'country': 'Country',
        'host': 'Host',
        'sub_region': 'SubRegion'
    }

    def __init__(self, action=None, country=None, host=None, sub_region=None, _configuration=None):  # noqa: E501
        """UpdateAreaBlockRuleRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._action = None
        self._country = None
        self._host = None
        self._sub_region = None
        self.discriminator = None

        self.action = action
        if country is not None:
            self.country = country
        self.host = host
        if sub_region is not None:
            self.sub_region = sub_region

    @property
    def action(self):
        """Gets the action of this UpdateAreaBlockRuleRequest.  # noqa: E501


        :return: The action of this UpdateAreaBlockRuleRequest.  # noqa: E501
        :rtype: str
        """
        return self._action

    @action.setter
    def action(self, action):
        """Sets the action of this UpdateAreaBlockRuleRequest.


        :param action: The action of this UpdateAreaBlockRuleRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and action is None:
            raise ValueError("Invalid value for `action`, must not be `None`")  # noqa: E501

        self._action = action

    @property
    def country(self):
        """Gets the country of this UpdateAreaBlockRuleRequest.  # noqa: E501


        :return: The country of this UpdateAreaBlockRuleRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._country

    @country.setter
    def country(self, country):
        """Sets the country of this UpdateAreaBlockRuleRequest.


        :param country: The country of this UpdateAreaBlockRuleRequest.  # noqa: E501
        :type: list[str]
        """

        self._country = country

    @property
    def host(self):
        """Gets the host of this UpdateAreaBlockRuleRequest.  # noqa: E501


        :return: The host of this UpdateAreaBlockRuleRequest.  # noqa: E501
        :rtype: str
        """
        return self._host

    @host.setter
    def host(self, host):
        """Sets the host of this UpdateAreaBlockRuleRequest.


        :param host: The host of this UpdateAreaBlockRuleRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and host is None:
            raise ValueError("Invalid value for `host`, must not be `None`")  # noqa: E501

        self._host = host

    @property
    def sub_region(self):
        """Gets the sub_region of this UpdateAreaBlockRuleRequest.  # noqa: E501


        :return: The sub_region of this UpdateAreaBlockRuleRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._sub_region

    @sub_region.setter
    def sub_region(self, sub_region):
        """Sets the sub_region of this UpdateAreaBlockRuleRequest.


        :param sub_region: The sub_region of this UpdateAreaBlockRuleRequest.  # noqa: E501
        :type: list[str]
        """

        self._sub_region = sub_region

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
        if issubclass(UpdateAreaBlockRuleRequest, dict):
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
        if not isinstance(other, UpdateAreaBlockRuleRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UpdateAreaBlockRuleRequest):
            return True

        return self.to_dict() != other.to_dict()
