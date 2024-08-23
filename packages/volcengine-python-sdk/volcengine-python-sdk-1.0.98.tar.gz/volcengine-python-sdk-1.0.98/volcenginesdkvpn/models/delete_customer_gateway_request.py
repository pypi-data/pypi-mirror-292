# coding: utf-8

"""
    vpn

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class DeleteCustomerGatewayRequest(object):
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
        'customer_gateway_id': 'str'
    }

    attribute_map = {
        'customer_gateway_id': 'CustomerGatewayId'
    }

    def __init__(self, customer_gateway_id=None, _configuration=None):  # noqa: E501
        """DeleteCustomerGatewayRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._customer_gateway_id = None
        self.discriminator = None

        self.customer_gateway_id = customer_gateway_id

    @property
    def customer_gateway_id(self):
        """Gets the customer_gateway_id of this DeleteCustomerGatewayRequest.  # noqa: E501


        :return: The customer_gateway_id of this DeleteCustomerGatewayRequest.  # noqa: E501
        :rtype: str
        """
        return self._customer_gateway_id

    @customer_gateway_id.setter
    def customer_gateway_id(self, customer_gateway_id):
        """Sets the customer_gateway_id of this DeleteCustomerGatewayRequest.


        :param customer_gateway_id: The customer_gateway_id of this DeleteCustomerGatewayRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and customer_gateway_id is None:
            raise ValueError("Invalid value for `customer_gateway_id`, must not be `None`")  # noqa: E501

        self._customer_gateway_id = customer_gateway_id

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
        if issubclass(DeleteCustomerGatewayRequest, dict):
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
        if not isinstance(other, DeleteCustomerGatewayRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DeleteCustomerGatewayRequest):
            return True

        return self.to_dict() != other.to_dict()
