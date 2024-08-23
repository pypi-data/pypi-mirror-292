# coding: utf-8

"""
    volc_observe

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class TopDataResultForGetTopDataOutput(object):
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
        'group_keys': 'dict(str, object)',
        'metric_data': 'dict(str, object)'
    }

    attribute_map = {
        'group_keys': 'GroupKeys',
        'metric_data': 'MetricData'
    }

    def __init__(self, group_keys=None, metric_data=None, _configuration=None):  # noqa: E501
        """TopDataResultForGetTopDataOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._group_keys = None
        self._metric_data = None
        self.discriminator = None

        if group_keys is not None:
            self.group_keys = group_keys
        if metric_data is not None:
            self.metric_data = metric_data

    @property
    def group_keys(self):
        """Gets the group_keys of this TopDataResultForGetTopDataOutput.  # noqa: E501


        :return: The group_keys of this TopDataResultForGetTopDataOutput.  # noqa: E501
        :rtype: dict(str, object)
        """
        return self._group_keys

    @group_keys.setter
    def group_keys(self, group_keys):
        """Sets the group_keys of this TopDataResultForGetTopDataOutput.


        :param group_keys: The group_keys of this TopDataResultForGetTopDataOutput.  # noqa: E501
        :type: dict(str, object)
        """

        self._group_keys = group_keys

    @property
    def metric_data(self):
        """Gets the metric_data of this TopDataResultForGetTopDataOutput.  # noqa: E501


        :return: The metric_data of this TopDataResultForGetTopDataOutput.  # noqa: E501
        :rtype: dict(str, object)
        """
        return self._metric_data

    @metric_data.setter
    def metric_data(self, metric_data):
        """Sets the metric_data of this TopDataResultForGetTopDataOutput.


        :param metric_data: The metric_data of this TopDataResultForGetTopDataOutput.  # noqa: E501
        :type: dict(str, object)
        """

        self._metric_data = metric_data

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
        if issubclass(TopDataResultForGetTopDataOutput, dict):
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
        if not isinstance(other, TopDataResultForGetTopDataOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TopDataResultForGetTopDataOutput):
            return True

        return self.to_dict() != other.to_dict()
