# coding: utf-8

"""
    vpc

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class TemporaryUpgradeEipAddressRequest(object):
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
        'allocation_id': 'str',
        'bandwidth': 'int',
        'period': 'int'
    }

    attribute_map = {
        'allocation_id': 'AllocationId',
        'bandwidth': 'Bandwidth',
        'period': 'Period'
    }

    def __init__(self, allocation_id=None, bandwidth=None, period=None, _configuration=None):  # noqa: E501
        """TemporaryUpgradeEipAddressRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._allocation_id = None
        self._bandwidth = None
        self._period = None
        self.discriminator = None

        self.allocation_id = allocation_id
        self.bandwidth = bandwidth
        self.period = period

    @property
    def allocation_id(self):
        """Gets the allocation_id of this TemporaryUpgradeEipAddressRequest.  # noqa: E501


        :return: The allocation_id of this TemporaryUpgradeEipAddressRequest.  # noqa: E501
        :rtype: str
        """
        return self._allocation_id

    @allocation_id.setter
    def allocation_id(self, allocation_id):
        """Sets the allocation_id of this TemporaryUpgradeEipAddressRequest.


        :param allocation_id: The allocation_id of this TemporaryUpgradeEipAddressRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and allocation_id is None:
            raise ValueError("Invalid value for `allocation_id`, must not be `None`")  # noqa: E501
        if (self._configuration.client_side_validation and
                allocation_id is not None and len(allocation_id) > 128):
            raise ValueError("Invalid value for `allocation_id`, length must be less than or equal to `128`")  # noqa: E501
        if (self._configuration.client_side_validation and
                allocation_id is not None and len(allocation_id) < 1):
            raise ValueError("Invalid value for `allocation_id`, length must be greater than or equal to `1`")  # noqa: E501

        self._allocation_id = allocation_id

    @property
    def bandwidth(self):
        """Gets the bandwidth of this TemporaryUpgradeEipAddressRequest.  # noqa: E501


        :return: The bandwidth of this TemporaryUpgradeEipAddressRequest.  # noqa: E501
        :rtype: int
        """
        return self._bandwidth

    @bandwidth.setter
    def bandwidth(self, bandwidth):
        """Sets the bandwidth of this TemporaryUpgradeEipAddressRequest.


        :param bandwidth: The bandwidth of this TemporaryUpgradeEipAddressRequest.  # noqa: E501
        :type: int
        """
        if self._configuration.client_side_validation and bandwidth is None:
            raise ValueError("Invalid value for `bandwidth`, must not be `None`")  # noqa: E501
        if (self._configuration.client_side_validation and
                bandwidth is not None and bandwidth < 1):  # noqa: E501
            raise ValueError("Invalid value for `bandwidth`, must be a value greater than or equal to `1`")  # noqa: E501

        self._bandwidth = bandwidth

    @property
    def period(self):
        """Gets the period of this TemporaryUpgradeEipAddressRequest.  # noqa: E501


        :return: The period of this TemporaryUpgradeEipAddressRequest.  # noqa: E501
        :rtype: int
        """
        return self._period

    @period.setter
    def period(self, period):
        """Sets the period of this TemporaryUpgradeEipAddressRequest.


        :param period: The period of this TemporaryUpgradeEipAddressRequest.  # noqa: E501
        :type: int
        """
        if self._configuration.client_side_validation and period is None:
            raise ValueError("Invalid value for `period`, must not be `None`")  # noqa: E501
        if (self._configuration.client_side_validation and
                period is not None and period > 720):  # noqa: E501
            raise ValueError("Invalid value for `period`, must be a value less than or equal to `720`")  # noqa: E501
        if (self._configuration.client_side_validation and
                period is not None and period < 1):  # noqa: E501
            raise ValueError("Invalid value for `period`, must be a value greater than or equal to `1`")  # noqa: E501

        self._period = period

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
        if issubclass(TemporaryUpgradeEipAddressRequest, dict):
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
        if not isinstance(other, TemporaryUpgradeEipAddressRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TemporaryUpgradeEipAddressRequest):
            return True

        return self.to_dict() != other.to_dict()
