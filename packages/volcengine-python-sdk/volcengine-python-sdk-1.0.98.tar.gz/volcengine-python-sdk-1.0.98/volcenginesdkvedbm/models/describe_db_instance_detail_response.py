# coding: utf-8

"""
    vedbm

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class DescribeDBInstanceDetailResponse(object):
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
        'charge_detail': 'ChargeDetailForDescribeDBInstanceDetailOutput',
        'endpoints': 'list[EndpointForDescribeDBInstanceDetailOutput]',
        'instance_detail': 'InstanceDetailForDescribeDBInstanceDetailOutput',
        'nodes': 'list[NodeForDescribeDBInstanceDetailOutput]',
        'tags': 'list[TagForDescribeDBInstanceDetailOutput]'
    }

    attribute_map = {
        'charge_detail': 'ChargeDetail',
        'endpoints': 'Endpoints',
        'instance_detail': 'InstanceDetail',
        'nodes': 'Nodes',
        'tags': 'Tags'
    }

    def __init__(self, charge_detail=None, endpoints=None, instance_detail=None, nodes=None, tags=None, _configuration=None):  # noqa: E501
        """DescribeDBInstanceDetailResponse - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._charge_detail = None
        self._endpoints = None
        self._instance_detail = None
        self._nodes = None
        self._tags = None
        self.discriminator = None

        if charge_detail is not None:
            self.charge_detail = charge_detail
        if endpoints is not None:
            self.endpoints = endpoints
        if instance_detail is not None:
            self.instance_detail = instance_detail
        if nodes is not None:
            self.nodes = nodes
        if tags is not None:
            self.tags = tags

    @property
    def charge_detail(self):
        """Gets the charge_detail of this DescribeDBInstanceDetailResponse.  # noqa: E501


        :return: The charge_detail of this DescribeDBInstanceDetailResponse.  # noqa: E501
        :rtype: ChargeDetailForDescribeDBInstanceDetailOutput
        """
        return self._charge_detail

    @charge_detail.setter
    def charge_detail(self, charge_detail):
        """Sets the charge_detail of this DescribeDBInstanceDetailResponse.


        :param charge_detail: The charge_detail of this DescribeDBInstanceDetailResponse.  # noqa: E501
        :type: ChargeDetailForDescribeDBInstanceDetailOutput
        """

        self._charge_detail = charge_detail

    @property
    def endpoints(self):
        """Gets the endpoints of this DescribeDBInstanceDetailResponse.  # noqa: E501


        :return: The endpoints of this DescribeDBInstanceDetailResponse.  # noqa: E501
        :rtype: list[EndpointForDescribeDBInstanceDetailOutput]
        """
        return self._endpoints

    @endpoints.setter
    def endpoints(self, endpoints):
        """Sets the endpoints of this DescribeDBInstanceDetailResponse.


        :param endpoints: The endpoints of this DescribeDBInstanceDetailResponse.  # noqa: E501
        :type: list[EndpointForDescribeDBInstanceDetailOutput]
        """

        self._endpoints = endpoints

    @property
    def instance_detail(self):
        """Gets the instance_detail of this DescribeDBInstanceDetailResponse.  # noqa: E501


        :return: The instance_detail of this DescribeDBInstanceDetailResponse.  # noqa: E501
        :rtype: InstanceDetailForDescribeDBInstanceDetailOutput
        """
        return self._instance_detail

    @instance_detail.setter
    def instance_detail(self, instance_detail):
        """Sets the instance_detail of this DescribeDBInstanceDetailResponse.


        :param instance_detail: The instance_detail of this DescribeDBInstanceDetailResponse.  # noqa: E501
        :type: InstanceDetailForDescribeDBInstanceDetailOutput
        """

        self._instance_detail = instance_detail

    @property
    def nodes(self):
        """Gets the nodes of this DescribeDBInstanceDetailResponse.  # noqa: E501


        :return: The nodes of this DescribeDBInstanceDetailResponse.  # noqa: E501
        :rtype: list[NodeForDescribeDBInstanceDetailOutput]
        """
        return self._nodes

    @nodes.setter
    def nodes(self, nodes):
        """Sets the nodes of this DescribeDBInstanceDetailResponse.


        :param nodes: The nodes of this DescribeDBInstanceDetailResponse.  # noqa: E501
        :type: list[NodeForDescribeDBInstanceDetailOutput]
        """

        self._nodes = nodes

    @property
    def tags(self):
        """Gets the tags of this DescribeDBInstanceDetailResponse.  # noqa: E501


        :return: The tags of this DescribeDBInstanceDetailResponse.  # noqa: E501
        :rtype: list[TagForDescribeDBInstanceDetailOutput]
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """Sets the tags of this DescribeDBInstanceDetailResponse.


        :param tags: The tags of this DescribeDBInstanceDetailResponse.  # noqa: E501
        :type: list[TagForDescribeDBInstanceDetailOutput]
        """

        self._tags = tags

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
        if issubclass(DescribeDBInstanceDetailResponse, dict):
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
        if not isinstance(other, DescribeDBInstanceDetailResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DescribeDBInstanceDetailResponse):
            return True

        return self.to_dict() != other.to_dict()
