# coding: utf-8

"""
    auto_scaling

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class AttachInstancesRequest(object):
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
        'entrusted': 'bool',
        'instance_ids': 'list[str]',
        'lifecycle_hook': 'bool',
        'scaling_group_id': 'str'
    }

    attribute_map = {
        'entrusted': 'Entrusted',
        'instance_ids': 'InstanceIds',
        'lifecycle_hook': 'LifecycleHook',
        'scaling_group_id': 'ScalingGroupId'
    }

    def __init__(self, entrusted=None, instance_ids=None, lifecycle_hook=None, scaling_group_id=None, _configuration=None):  # noqa: E501
        """AttachInstancesRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._entrusted = None
        self._instance_ids = None
        self._lifecycle_hook = None
        self._scaling_group_id = None
        self.discriminator = None

        if entrusted is not None:
            self.entrusted = entrusted
        if instance_ids is not None:
            self.instance_ids = instance_ids
        if lifecycle_hook is not None:
            self.lifecycle_hook = lifecycle_hook
        self.scaling_group_id = scaling_group_id

    @property
    def entrusted(self):
        """Gets the entrusted of this AttachInstancesRequest.  # noqa: E501


        :return: The entrusted of this AttachInstancesRequest.  # noqa: E501
        :rtype: bool
        """
        return self._entrusted

    @entrusted.setter
    def entrusted(self, entrusted):
        """Sets the entrusted of this AttachInstancesRequest.


        :param entrusted: The entrusted of this AttachInstancesRequest.  # noqa: E501
        :type: bool
        """

        self._entrusted = entrusted

    @property
    def instance_ids(self):
        """Gets the instance_ids of this AttachInstancesRequest.  # noqa: E501


        :return: The instance_ids of this AttachInstancesRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._instance_ids

    @instance_ids.setter
    def instance_ids(self, instance_ids):
        """Sets the instance_ids of this AttachInstancesRequest.


        :param instance_ids: The instance_ids of this AttachInstancesRequest.  # noqa: E501
        :type: list[str]
        """

        self._instance_ids = instance_ids

    @property
    def lifecycle_hook(self):
        """Gets the lifecycle_hook of this AttachInstancesRequest.  # noqa: E501


        :return: The lifecycle_hook of this AttachInstancesRequest.  # noqa: E501
        :rtype: bool
        """
        return self._lifecycle_hook

    @lifecycle_hook.setter
    def lifecycle_hook(self, lifecycle_hook):
        """Sets the lifecycle_hook of this AttachInstancesRequest.


        :param lifecycle_hook: The lifecycle_hook of this AttachInstancesRequest.  # noqa: E501
        :type: bool
        """

        self._lifecycle_hook = lifecycle_hook

    @property
    def scaling_group_id(self):
        """Gets the scaling_group_id of this AttachInstancesRequest.  # noqa: E501


        :return: The scaling_group_id of this AttachInstancesRequest.  # noqa: E501
        :rtype: str
        """
        return self._scaling_group_id

    @scaling_group_id.setter
    def scaling_group_id(self, scaling_group_id):
        """Sets the scaling_group_id of this AttachInstancesRequest.


        :param scaling_group_id: The scaling_group_id of this AttachInstancesRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and scaling_group_id is None:
            raise ValueError("Invalid value for `scaling_group_id`, must not be `None`")  # noqa: E501

        self._scaling_group_id = scaling_group_id

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
        if issubclass(AttachInstancesRequest, dict):
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
        if not isinstance(other, AttachInstancesRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AttachInstancesRequest):
            return True

        return self.to_dict() != other.to_dict()
