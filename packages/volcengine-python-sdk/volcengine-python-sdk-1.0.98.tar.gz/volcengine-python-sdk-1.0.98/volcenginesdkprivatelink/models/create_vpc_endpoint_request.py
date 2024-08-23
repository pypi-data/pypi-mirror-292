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


class CreateVpcEndpointRequest(object):
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
        'client_token': 'str',
        'description': 'str',
        'endpoint_name': 'str',
        'private_dns_enabled': 'str',
        'project_name': 'str',
        'security_group_ids': 'list[str]',
        'service_id': 'str',
        'service_name': 'str',
        'tags': 'list[TagForCreateVpcEndpointInput]',
        'vpc_id': 'str',
        'zones': 'list[ZoneForCreateVpcEndpointInput]'
    }

    attribute_map = {
        'client_token': 'ClientToken',
        'description': 'Description',
        'endpoint_name': 'EndpointName',
        'private_dns_enabled': 'PrivateDNSEnabled',
        'project_name': 'ProjectName',
        'security_group_ids': 'SecurityGroupIds',
        'service_id': 'ServiceId',
        'service_name': 'ServiceName',
        'tags': 'Tags',
        'vpc_id': 'VpcId',
        'zones': 'Zones'
    }

    def __init__(self, client_token=None, description=None, endpoint_name=None, private_dns_enabled=None, project_name=None, security_group_ids=None, service_id=None, service_name=None, tags=None, vpc_id=None, zones=None, _configuration=None):  # noqa: E501
        """CreateVpcEndpointRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._client_token = None
        self._description = None
        self._endpoint_name = None
        self._private_dns_enabled = None
        self._project_name = None
        self._security_group_ids = None
        self._service_id = None
        self._service_name = None
        self._tags = None
        self._vpc_id = None
        self._zones = None
        self.discriminator = None

        if client_token is not None:
            self.client_token = client_token
        if description is not None:
            self.description = description
        if endpoint_name is not None:
            self.endpoint_name = endpoint_name
        if private_dns_enabled is not None:
            self.private_dns_enabled = private_dns_enabled
        if project_name is not None:
            self.project_name = project_name
        if security_group_ids is not None:
            self.security_group_ids = security_group_ids
        self.service_id = service_id
        if service_name is not None:
            self.service_name = service_name
        if tags is not None:
            self.tags = tags
        self.vpc_id = vpc_id
        if zones is not None:
            self.zones = zones

    @property
    def client_token(self):
        """Gets the client_token of this CreateVpcEndpointRequest.  # noqa: E501


        :return: The client_token of this CreateVpcEndpointRequest.  # noqa: E501
        :rtype: str
        """
        return self._client_token

    @client_token.setter
    def client_token(self, client_token):
        """Sets the client_token of this CreateVpcEndpointRequest.


        :param client_token: The client_token of this CreateVpcEndpointRequest.  # noqa: E501
        :type: str
        """

        self._client_token = client_token

    @property
    def description(self):
        """Gets the description of this CreateVpcEndpointRequest.  # noqa: E501


        :return: The description of this CreateVpcEndpointRequest.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this CreateVpcEndpointRequest.


        :param description: The description of this CreateVpcEndpointRequest.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def endpoint_name(self):
        """Gets the endpoint_name of this CreateVpcEndpointRequest.  # noqa: E501


        :return: The endpoint_name of this CreateVpcEndpointRequest.  # noqa: E501
        :rtype: str
        """
        return self._endpoint_name

    @endpoint_name.setter
    def endpoint_name(self, endpoint_name):
        """Sets the endpoint_name of this CreateVpcEndpointRequest.


        :param endpoint_name: The endpoint_name of this CreateVpcEndpointRequest.  # noqa: E501
        :type: str
        """

        self._endpoint_name = endpoint_name

    @property
    def private_dns_enabled(self):
        """Gets the private_dns_enabled of this CreateVpcEndpointRequest.  # noqa: E501


        :return: The private_dns_enabled of this CreateVpcEndpointRequest.  # noqa: E501
        :rtype: str
        """
        return self._private_dns_enabled

    @private_dns_enabled.setter
    def private_dns_enabled(self, private_dns_enabled):
        """Sets the private_dns_enabled of this CreateVpcEndpointRequest.


        :param private_dns_enabled: The private_dns_enabled of this CreateVpcEndpointRequest.  # noqa: E501
        :type: str
        """

        self._private_dns_enabled = private_dns_enabled

    @property
    def project_name(self):
        """Gets the project_name of this CreateVpcEndpointRequest.  # noqa: E501


        :return: The project_name of this CreateVpcEndpointRequest.  # noqa: E501
        :rtype: str
        """
        return self._project_name

    @project_name.setter
    def project_name(self, project_name):
        """Sets the project_name of this CreateVpcEndpointRequest.


        :param project_name: The project_name of this CreateVpcEndpointRequest.  # noqa: E501
        :type: str
        """

        self._project_name = project_name

    @property
    def security_group_ids(self):
        """Gets the security_group_ids of this CreateVpcEndpointRequest.  # noqa: E501


        :return: The security_group_ids of this CreateVpcEndpointRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._security_group_ids

    @security_group_ids.setter
    def security_group_ids(self, security_group_ids):
        """Sets the security_group_ids of this CreateVpcEndpointRequest.


        :param security_group_ids: The security_group_ids of this CreateVpcEndpointRequest.  # noqa: E501
        :type: list[str]
        """

        self._security_group_ids = security_group_ids

    @property
    def service_id(self):
        """Gets the service_id of this CreateVpcEndpointRequest.  # noqa: E501


        :return: The service_id of this CreateVpcEndpointRequest.  # noqa: E501
        :rtype: str
        """
        return self._service_id

    @service_id.setter
    def service_id(self, service_id):
        """Sets the service_id of this CreateVpcEndpointRequest.


        :param service_id: The service_id of this CreateVpcEndpointRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and service_id is None:
            raise ValueError("Invalid value for `service_id`, must not be `None`")  # noqa: E501

        self._service_id = service_id

    @property
    def service_name(self):
        """Gets the service_name of this CreateVpcEndpointRequest.  # noqa: E501


        :return: The service_name of this CreateVpcEndpointRequest.  # noqa: E501
        :rtype: str
        """
        return self._service_name

    @service_name.setter
    def service_name(self, service_name):
        """Sets the service_name of this CreateVpcEndpointRequest.


        :param service_name: The service_name of this CreateVpcEndpointRequest.  # noqa: E501
        :type: str
        """

        self._service_name = service_name

    @property
    def tags(self):
        """Gets the tags of this CreateVpcEndpointRequest.  # noqa: E501


        :return: The tags of this CreateVpcEndpointRequest.  # noqa: E501
        :rtype: list[TagForCreateVpcEndpointInput]
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """Sets the tags of this CreateVpcEndpointRequest.


        :param tags: The tags of this CreateVpcEndpointRequest.  # noqa: E501
        :type: list[TagForCreateVpcEndpointInput]
        """

        self._tags = tags

    @property
    def vpc_id(self):
        """Gets the vpc_id of this CreateVpcEndpointRequest.  # noqa: E501


        :return: The vpc_id of this CreateVpcEndpointRequest.  # noqa: E501
        :rtype: str
        """
        return self._vpc_id

    @vpc_id.setter
    def vpc_id(self, vpc_id):
        """Sets the vpc_id of this CreateVpcEndpointRequest.


        :param vpc_id: The vpc_id of this CreateVpcEndpointRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and vpc_id is None:
            raise ValueError("Invalid value for `vpc_id`, must not be `None`")  # noqa: E501

        self._vpc_id = vpc_id

    @property
    def zones(self):
        """Gets the zones of this CreateVpcEndpointRequest.  # noqa: E501


        :return: The zones of this CreateVpcEndpointRequest.  # noqa: E501
        :rtype: list[ZoneForCreateVpcEndpointInput]
        """
        return self._zones

    @zones.setter
    def zones(self, zones):
        """Sets the zones of this CreateVpcEndpointRequest.


        :param zones: The zones of this CreateVpcEndpointRequest.  # noqa: E501
        :type: list[ZoneForCreateVpcEndpointInput]
        """

        self._zones = zones

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
        if issubclass(CreateVpcEndpointRequest, dict):
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
        if not isinstance(other, CreateVpcEndpointRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateVpcEndpointRequest):
            return True

        return self.to_dict() != other.to_dict()
