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


class GpuForDescribeSpotAdviceInput(object):
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
        'count': 'int',
        'product_name': 'str'
    }

    attribute_map = {
        'count': 'Count',
        'product_name': 'ProductName'
    }

    def __init__(self, count=None, product_name=None, _configuration=None):  # noqa: E501
        """GpuForDescribeSpotAdviceInput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._count = None
        self._product_name = None
        self.discriminator = None

        if count is not None:
            self.count = count
        if product_name is not None:
            self.product_name = product_name

    @property
    def count(self):
        """Gets the count of this GpuForDescribeSpotAdviceInput.  # noqa: E501


        :return: The count of this GpuForDescribeSpotAdviceInput.  # noqa: E501
        :rtype: int
        """
        return self._count

    @count.setter
    def count(self, count):
        """Sets the count of this GpuForDescribeSpotAdviceInput.


        :param count: The count of this GpuForDescribeSpotAdviceInput.  # noqa: E501
        :type: int
        """

        self._count = count

    @property
    def product_name(self):
        """Gets the product_name of this GpuForDescribeSpotAdviceInput.  # noqa: E501


        :return: The product_name of this GpuForDescribeSpotAdviceInput.  # noqa: E501
        :rtype: str
        """
        return self._product_name

    @product_name.setter
    def product_name(self, product_name):
        """Sets the product_name of this GpuForDescribeSpotAdviceInput.


        :param product_name: The product_name of this GpuForDescribeSpotAdviceInput.  # noqa: E501
        :type: str
        """

        self._product_name = product_name

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
        if issubclass(GpuForDescribeSpotAdviceInput, dict):
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
        if not isinstance(other, GpuForDescribeSpotAdviceInput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, GpuForDescribeSpotAdviceInput):
            return True

        return self.to_dict() != other.to_dict()
