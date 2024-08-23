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


class DescribeVpcGatewayEndpointAttributesResponse(object):
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
        'creation_time': 'str',
        'description': 'str',
        'endpoint_id': 'str',
        'endpoint_name': 'str',
        'project_name': 'str',
        'request_id': 'str',
        'service_id': 'str',
        'service_name': 'str',
        'status': 'str',
        'tags': 'list[TagForDescribeVpcGatewayEndpointAttributesOutput]',
        'update_time': 'str',
        'vpc_id': 'str',
        'vpc_policy': 'str'
    }

    attribute_map = {
        'creation_time': 'CreationTime',
        'description': 'Description',
        'endpoint_id': 'EndpointId',
        'endpoint_name': 'EndpointName',
        'project_name': 'ProjectName',
        'request_id': 'RequestId',
        'service_id': 'ServiceId',
        'service_name': 'ServiceName',
        'status': 'Status',
        'tags': 'Tags',
        'update_time': 'UpdateTime',
        'vpc_id': 'VpcId',
        'vpc_policy': 'VpcPolicy'
    }

    def __init__(self, creation_time=None, description=None, endpoint_id=None, endpoint_name=None, project_name=None, request_id=None, service_id=None, service_name=None, status=None, tags=None, update_time=None, vpc_id=None, vpc_policy=None, _configuration=None):  # noqa: E501
        """DescribeVpcGatewayEndpointAttributesResponse - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._creation_time = None
        self._description = None
        self._endpoint_id = None
        self._endpoint_name = None
        self._project_name = None
        self._request_id = None
        self._service_id = None
        self._service_name = None
        self._status = None
        self._tags = None
        self._update_time = None
        self._vpc_id = None
        self._vpc_policy = None
        self.discriminator = None

        if creation_time is not None:
            self.creation_time = creation_time
        if description is not None:
            self.description = description
        if endpoint_id is not None:
            self.endpoint_id = endpoint_id
        if endpoint_name is not None:
            self.endpoint_name = endpoint_name
        if project_name is not None:
            self.project_name = project_name
        if request_id is not None:
            self.request_id = request_id
        if service_id is not None:
            self.service_id = service_id
        if service_name is not None:
            self.service_name = service_name
        if status is not None:
            self.status = status
        if tags is not None:
            self.tags = tags
        if update_time is not None:
            self.update_time = update_time
        if vpc_id is not None:
            self.vpc_id = vpc_id
        if vpc_policy is not None:
            self.vpc_policy = vpc_policy

    @property
    def creation_time(self):
        """Gets the creation_time of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501


        :return: The creation_time of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._creation_time

    @creation_time.setter
    def creation_time(self, creation_time):
        """Sets the creation_time of this DescribeVpcGatewayEndpointAttributesResponse.


        :param creation_time: The creation_time of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :type: str
        """

        self._creation_time = creation_time

    @property
    def description(self):
        """Gets the description of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501


        :return: The description of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this DescribeVpcGatewayEndpointAttributesResponse.


        :param description: The description of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def endpoint_id(self):
        """Gets the endpoint_id of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501


        :return: The endpoint_id of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._endpoint_id

    @endpoint_id.setter
    def endpoint_id(self, endpoint_id):
        """Sets the endpoint_id of this DescribeVpcGatewayEndpointAttributesResponse.


        :param endpoint_id: The endpoint_id of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :type: str
        """

        self._endpoint_id = endpoint_id

    @property
    def endpoint_name(self):
        """Gets the endpoint_name of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501


        :return: The endpoint_name of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._endpoint_name

    @endpoint_name.setter
    def endpoint_name(self, endpoint_name):
        """Sets the endpoint_name of this DescribeVpcGatewayEndpointAttributesResponse.


        :param endpoint_name: The endpoint_name of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :type: str
        """

        self._endpoint_name = endpoint_name

    @property
    def project_name(self):
        """Gets the project_name of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501


        :return: The project_name of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._project_name

    @project_name.setter
    def project_name(self, project_name):
        """Sets the project_name of this DescribeVpcGatewayEndpointAttributesResponse.


        :param project_name: The project_name of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :type: str
        """

        self._project_name = project_name

    @property
    def request_id(self):
        """Gets the request_id of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501


        :return: The request_id of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._request_id

    @request_id.setter
    def request_id(self, request_id):
        """Sets the request_id of this DescribeVpcGatewayEndpointAttributesResponse.


        :param request_id: The request_id of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :type: str
        """

        self._request_id = request_id

    @property
    def service_id(self):
        """Gets the service_id of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501


        :return: The service_id of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._service_id

    @service_id.setter
    def service_id(self, service_id):
        """Sets the service_id of this DescribeVpcGatewayEndpointAttributesResponse.


        :param service_id: The service_id of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :type: str
        """

        self._service_id = service_id

    @property
    def service_name(self):
        """Gets the service_name of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501


        :return: The service_name of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._service_name

    @service_name.setter
    def service_name(self, service_name):
        """Sets the service_name of this DescribeVpcGatewayEndpointAttributesResponse.


        :param service_name: The service_name of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :type: str
        """

        self._service_name = service_name

    @property
    def status(self):
        """Gets the status of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501


        :return: The status of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this DescribeVpcGatewayEndpointAttributesResponse.


        :param status: The status of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def tags(self):
        """Gets the tags of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501


        :return: The tags of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :rtype: list[TagForDescribeVpcGatewayEndpointAttributesOutput]
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """Sets the tags of this DescribeVpcGatewayEndpointAttributesResponse.


        :param tags: The tags of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :type: list[TagForDescribeVpcGatewayEndpointAttributesOutput]
        """

        self._tags = tags

    @property
    def update_time(self):
        """Gets the update_time of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501


        :return: The update_time of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._update_time

    @update_time.setter
    def update_time(self, update_time):
        """Sets the update_time of this DescribeVpcGatewayEndpointAttributesResponse.


        :param update_time: The update_time of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :type: str
        """

        self._update_time = update_time

    @property
    def vpc_id(self):
        """Gets the vpc_id of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501


        :return: The vpc_id of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._vpc_id

    @vpc_id.setter
    def vpc_id(self, vpc_id):
        """Sets the vpc_id of this DescribeVpcGatewayEndpointAttributesResponse.


        :param vpc_id: The vpc_id of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :type: str
        """

        self._vpc_id = vpc_id

    @property
    def vpc_policy(self):
        """Gets the vpc_policy of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501


        :return: The vpc_policy of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :rtype: str
        """
        return self._vpc_policy

    @vpc_policy.setter
    def vpc_policy(self, vpc_policy):
        """Sets the vpc_policy of this DescribeVpcGatewayEndpointAttributesResponse.


        :param vpc_policy: The vpc_policy of this DescribeVpcGatewayEndpointAttributesResponse.  # noqa: E501
        :type: str
        """

        self._vpc_policy = vpc_policy

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
        if issubclass(DescribeVpcGatewayEndpointAttributesResponse, dict):
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
        if not isinstance(other, DescribeVpcGatewayEndpointAttributesResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DescribeVpcGatewayEndpointAttributesResponse):
            return True

        return self.to_dict() != other.to_dict()
