# coding: utf-8

"""
    mcdn

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class SubmitPreloadTaskResponse(object):
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
        'task_id': 'str',
        'task_ids': 'list[str]'
    }

    attribute_map = {
        'task_id': 'TaskId',
        'task_ids': 'TaskIds'
    }

    def __init__(self, task_id=None, task_ids=None, _configuration=None):  # noqa: E501
        """SubmitPreloadTaskResponse - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._task_id = None
        self._task_ids = None
        self.discriminator = None

        if task_id is not None:
            self.task_id = task_id
        if task_ids is not None:
            self.task_ids = task_ids

    @property
    def task_id(self):
        """Gets the task_id of this SubmitPreloadTaskResponse.  # noqa: E501


        :return: The task_id of this SubmitPreloadTaskResponse.  # noqa: E501
        :rtype: str
        """
        return self._task_id

    @task_id.setter
    def task_id(self, task_id):
        """Sets the task_id of this SubmitPreloadTaskResponse.


        :param task_id: The task_id of this SubmitPreloadTaskResponse.  # noqa: E501
        :type: str
        """

        self._task_id = task_id

    @property
    def task_ids(self):
        """Gets the task_ids of this SubmitPreloadTaskResponse.  # noqa: E501


        :return: The task_ids of this SubmitPreloadTaskResponse.  # noqa: E501
        :rtype: list[str]
        """
        return self._task_ids

    @task_ids.setter
    def task_ids(self, task_ids):
        """Sets the task_ids of this SubmitPreloadTaskResponse.


        :param task_ids: The task_ids of this SubmitPreloadTaskResponse.  # noqa: E501
        :type: list[str]
        """

        self._task_ids = task_ids

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
        if issubclass(SubmitPreloadTaskResponse, dict):
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
        if not isinstance(other, SubmitPreloadTaskResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SubmitPreloadTaskResponse):
            return True

        return self.to_dict() != other.to_dict()
