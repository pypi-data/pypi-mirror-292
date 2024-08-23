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


class OriginForDescribeCdnConfigOutput(object):
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
        'condition': 'ConditionForDescribeCdnConfigOutput',
        'origin_action': 'OriginActionForDescribeCdnConfigOutput'
    }

    attribute_map = {
        'condition': 'Condition',
        'origin_action': 'OriginAction'
    }

    def __init__(self, condition=None, origin_action=None, _configuration=None):  # noqa: E501
        """OriginForDescribeCdnConfigOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._condition = None
        self._origin_action = None
        self.discriminator = None

        if condition is not None:
            self.condition = condition
        if origin_action is not None:
            self.origin_action = origin_action

    @property
    def condition(self):
        """Gets the condition of this OriginForDescribeCdnConfigOutput.  # noqa: E501


        :return: The condition of this OriginForDescribeCdnConfigOutput.  # noqa: E501
        :rtype: ConditionForDescribeCdnConfigOutput
        """
        return self._condition

    @condition.setter
    def condition(self, condition):
        """Sets the condition of this OriginForDescribeCdnConfigOutput.


        :param condition: The condition of this OriginForDescribeCdnConfigOutput.  # noqa: E501
        :type: ConditionForDescribeCdnConfigOutput
        """

        self._condition = condition

    @property
    def origin_action(self):
        """Gets the origin_action of this OriginForDescribeCdnConfigOutput.  # noqa: E501


        :return: The origin_action of this OriginForDescribeCdnConfigOutput.  # noqa: E501
        :rtype: OriginActionForDescribeCdnConfigOutput
        """
        return self._origin_action

    @origin_action.setter
    def origin_action(self, origin_action):
        """Sets the origin_action of this OriginForDescribeCdnConfigOutput.


        :param origin_action: The origin_action of this OriginForDescribeCdnConfigOutput.  # noqa: E501
        :type: OriginActionForDescribeCdnConfigOutput
        """

        self._origin_action = origin_action

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
        if issubclass(OriginForDescribeCdnConfigOutput, dict):
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
        if not isinstance(other, OriginForDescribeCdnConfigOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, OriginForDescribeCdnConfigOutput):
            return True

        return self.to_dict() != other.to_dict()
