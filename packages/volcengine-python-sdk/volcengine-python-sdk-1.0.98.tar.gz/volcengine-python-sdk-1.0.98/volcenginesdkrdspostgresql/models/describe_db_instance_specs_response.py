# coding: utf-8

"""
    rds_postgresql

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class DescribeDBInstanceSpecsResponse(object):
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
        'instance_specs': 'list[InstanceSpecForDescribeDBInstanceSpecsOutput]',
        'total': 'int'
    }

    attribute_map = {
        'instance_specs': 'InstanceSpecs',
        'total': 'Total'
    }

    def __init__(self, instance_specs=None, total=None, _configuration=None):  # noqa: E501
        """DescribeDBInstanceSpecsResponse - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._instance_specs = None
        self._total = None
        self.discriminator = None

        if instance_specs is not None:
            self.instance_specs = instance_specs
        if total is not None:
            self.total = total

    @property
    def instance_specs(self):
        """Gets the instance_specs of this DescribeDBInstanceSpecsResponse.  # noqa: E501


        :return: The instance_specs of this DescribeDBInstanceSpecsResponse.  # noqa: E501
        :rtype: list[InstanceSpecForDescribeDBInstanceSpecsOutput]
        """
        return self._instance_specs

    @instance_specs.setter
    def instance_specs(self, instance_specs):
        """Sets the instance_specs of this DescribeDBInstanceSpecsResponse.


        :param instance_specs: The instance_specs of this DescribeDBInstanceSpecsResponse.  # noqa: E501
        :type: list[InstanceSpecForDescribeDBInstanceSpecsOutput]
        """

        self._instance_specs = instance_specs

    @property
    def total(self):
        """Gets the total of this DescribeDBInstanceSpecsResponse.  # noqa: E501


        :return: The total of this DescribeDBInstanceSpecsResponse.  # noqa: E501
        :rtype: int
        """
        return self._total

    @total.setter
    def total(self, total):
        """Sets the total of this DescribeDBInstanceSpecsResponse.


        :param total: The total of this DescribeDBInstanceSpecsResponse.  # noqa: E501
        :type: int
        """

        self._total = total

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
        if issubclass(DescribeDBInstanceSpecsResponse, dict):
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
        if not isinstance(other, DescribeDBInstanceSpecsResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DescribeDBInstanceSpecsResponse):
            return True

        return self.to_dict() != other.to_dict()
