# coding: utf-8

"""
    privatelink

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class DescribeVpcEndpointServicesRequest(object):
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
        'page_number': 'int',
        'page_size': 'int',
        'project_name': 'str',
        'service_ids': 'list[str]',
        'service_name': 'str',
        'service_resource_type': 'str',
        'tag_filters': 'list[TagFilterForDescribeVpcEndpointServicesInput]'
    }

    attribute_map = {
        'page_number': 'PageNumber',
        'page_size': 'PageSize',
        'project_name': 'ProjectName',
        'service_ids': 'ServiceIds',
        'service_name': 'ServiceName',
        'service_resource_type': 'ServiceResourceType',
        'tag_filters': 'TagFilters'
    }

    def __init__(self, page_number=None, page_size=None, project_name=None, service_ids=None, service_name=None, service_resource_type=None, tag_filters=None, _configuration=None):  # noqa: E501
        """DescribeVpcEndpointServicesRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._page_number = None
        self._page_size = None
        self._project_name = None
        self._service_ids = None
        self._service_name = None
        self._service_resource_type = None
        self._tag_filters = None
        self.discriminator = None

        if page_number is not None:
            self.page_number = page_number
        if page_size is not None:
            self.page_size = page_size
        if project_name is not None:
            self.project_name = project_name
        if service_ids is not None:
            self.service_ids = service_ids
        if service_name is not None:
            self.service_name = service_name
        if service_resource_type is not None:
            self.service_resource_type = service_resource_type
        if tag_filters is not None:
            self.tag_filters = tag_filters

    @property
    def page_number(self):
        """Gets the page_number of this DescribeVpcEndpointServicesRequest.  # noqa: E501


        :return: The page_number of this DescribeVpcEndpointServicesRequest.  # noqa: E501
        :rtype: int
        """
        return self._page_number

    @page_number.setter
    def page_number(self, page_number):
        """Sets the page_number of this DescribeVpcEndpointServicesRequest.


        :param page_number: The page_number of this DescribeVpcEndpointServicesRequest.  # noqa: E501
        :type: int
        """

        self._page_number = page_number

    @property
    def page_size(self):
        """Gets the page_size of this DescribeVpcEndpointServicesRequest.  # noqa: E501


        :return: The page_size of this DescribeVpcEndpointServicesRequest.  # noqa: E501
        :rtype: int
        """
        return self._page_size

    @page_size.setter
    def page_size(self, page_size):
        """Sets the page_size of this DescribeVpcEndpointServicesRequest.


        :param page_size: The page_size of this DescribeVpcEndpointServicesRequest.  # noqa: E501
        :type: int
        """

        self._page_size = page_size

    @property
    def project_name(self):
        """Gets the project_name of this DescribeVpcEndpointServicesRequest.  # noqa: E501


        :return: The project_name of this DescribeVpcEndpointServicesRequest.  # noqa: E501
        :rtype: str
        """
        return self._project_name

    @project_name.setter
    def project_name(self, project_name):
        """Sets the project_name of this DescribeVpcEndpointServicesRequest.


        :param project_name: The project_name of this DescribeVpcEndpointServicesRequest.  # noqa: E501
        :type: str
        """

        self._project_name = project_name

    @property
    def service_ids(self):
        """Gets the service_ids of this DescribeVpcEndpointServicesRequest.  # noqa: E501


        :return: The service_ids of this DescribeVpcEndpointServicesRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._service_ids

    @service_ids.setter
    def service_ids(self, service_ids):
        """Sets the service_ids of this DescribeVpcEndpointServicesRequest.


        :param service_ids: The service_ids of this DescribeVpcEndpointServicesRequest.  # noqa: E501
        :type: list[str]
        """

        self._service_ids = service_ids

    @property
    def service_name(self):
        """Gets the service_name of this DescribeVpcEndpointServicesRequest.  # noqa: E501


        :return: The service_name of this DescribeVpcEndpointServicesRequest.  # noqa: E501
        :rtype: str
        """
        return self._service_name

    @service_name.setter
    def service_name(self, service_name):
        """Sets the service_name of this DescribeVpcEndpointServicesRequest.


        :param service_name: The service_name of this DescribeVpcEndpointServicesRequest.  # noqa: E501
        :type: str
        """

        self._service_name = service_name

    @property
    def service_resource_type(self):
        """Gets the service_resource_type of this DescribeVpcEndpointServicesRequest.  # noqa: E501


        :return: The service_resource_type of this DescribeVpcEndpointServicesRequest.  # noqa: E501
        :rtype: str
        """
        return self._service_resource_type

    @service_resource_type.setter
    def service_resource_type(self, service_resource_type):
        """Sets the service_resource_type of this DescribeVpcEndpointServicesRequest.


        :param service_resource_type: The service_resource_type of this DescribeVpcEndpointServicesRequest.  # noqa: E501
        :type: str
        """

        self._service_resource_type = service_resource_type

    @property
    def tag_filters(self):
        """Gets the tag_filters of this DescribeVpcEndpointServicesRequest.  # noqa: E501


        :return: The tag_filters of this DescribeVpcEndpointServicesRequest.  # noqa: E501
        :rtype: list[TagFilterForDescribeVpcEndpointServicesInput]
        """
        return self._tag_filters

    @tag_filters.setter
    def tag_filters(self, tag_filters):
        """Sets the tag_filters of this DescribeVpcEndpointServicesRequest.


        :param tag_filters: The tag_filters of this DescribeVpcEndpointServicesRequest.  # noqa: E501
        :type: list[TagFilterForDescribeVpcEndpointServicesInput]
        """

        self._tag_filters = tag_filters

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
        if issubclass(DescribeVpcEndpointServicesRequest, dict):
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
        if not isinstance(other, DescribeVpcEndpointServicesRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DescribeVpcEndpointServicesRequest):
            return True

        return self.to_dict() != other.to_dict()
