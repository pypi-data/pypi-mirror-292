# coding: utf-8

"""
    vke

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class PublicAccessNetworkConfigForCreateClusterInput(object):
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
        'bandwidth': 'int',
        'billing_type': 'int',
        'isp': 'str'
    }

    attribute_map = {
        'bandwidth': 'Bandwidth',
        'billing_type': 'BillingType',
        'isp': 'Isp'
    }

    def __init__(self, bandwidth=None, billing_type=None, isp=None, _configuration=None):  # noqa: E501
        """PublicAccessNetworkConfigForCreateClusterInput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._bandwidth = None
        self._billing_type = None
        self._isp = None
        self.discriminator = None

        if bandwidth is not None:
            self.bandwidth = bandwidth
        if billing_type is not None:
            self.billing_type = billing_type
        if isp is not None:
            self.isp = isp

    @property
    def bandwidth(self):
        """Gets the bandwidth of this PublicAccessNetworkConfigForCreateClusterInput.  # noqa: E501


        :return: The bandwidth of this PublicAccessNetworkConfigForCreateClusterInput.  # noqa: E501
        :rtype: int
        """
        return self._bandwidth

    @bandwidth.setter
    def bandwidth(self, bandwidth):
        """Sets the bandwidth of this PublicAccessNetworkConfigForCreateClusterInput.


        :param bandwidth: The bandwidth of this PublicAccessNetworkConfigForCreateClusterInput.  # noqa: E501
        :type: int
        """

        self._bandwidth = bandwidth

    @property
    def billing_type(self):
        """Gets the billing_type of this PublicAccessNetworkConfigForCreateClusterInput.  # noqa: E501


        :return: The billing_type of this PublicAccessNetworkConfigForCreateClusterInput.  # noqa: E501
        :rtype: int
        """
        return self._billing_type

    @billing_type.setter
    def billing_type(self, billing_type):
        """Sets the billing_type of this PublicAccessNetworkConfigForCreateClusterInput.


        :param billing_type: The billing_type of this PublicAccessNetworkConfigForCreateClusterInput.  # noqa: E501
        :type: int
        """

        self._billing_type = billing_type

    @property
    def isp(self):
        """Gets the isp of this PublicAccessNetworkConfigForCreateClusterInput.  # noqa: E501


        :return: The isp of this PublicAccessNetworkConfigForCreateClusterInput.  # noqa: E501
        :rtype: str
        """
        return self._isp

    @isp.setter
    def isp(self, isp):
        """Sets the isp of this PublicAccessNetworkConfigForCreateClusterInput.


        :param isp: The isp of this PublicAccessNetworkConfigForCreateClusterInput.  # noqa: E501
        :type: str
        """
        allowed_values = ["BGP", "ChinaMobile", "ChinaTelecom", "ChinaUnicom"]  # noqa: E501
        if (self._configuration.client_side_validation and
                isp not in allowed_values):
            raise ValueError(
                "Invalid value for `isp` ({0}), must be one of {1}"  # noqa: E501
                .format(isp, allowed_values)
            )

        self._isp = isp

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
        if issubclass(PublicAccessNetworkConfigForCreateClusterInput, dict):
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
        if not isinstance(other, PublicAccessNetworkConfigForCreateClusterInput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, PublicAccessNetworkConfigForCreateClusterInput):
            return True

        return self.to_dict() != other.to_dict()
