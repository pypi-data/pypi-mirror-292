# coding: utf-8

"""
    filenas

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class UpdateFileSystemRequest(object):
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
        'auto_expand': 'bool',
        'auto_expand_limit': 'int',
        'auto_expand_step': 'int',
        'auto_expand_threshold': 'int',
        'description': 'str',
        'file_system_id': 'str',
        'file_system_name': 'str',
        'project_name': 'str',
        'tags': 'list[TagForUpdateFileSystemInput]'
    }

    attribute_map = {
        'auto_expand': 'AutoExpand',
        'auto_expand_limit': 'AutoExpandLimit',
        'auto_expand_step': 'AutoExpandStep',
        'auto_expand_threshold': 'AutoExpandThreshold',
        'description': 'Description',
        'file_system_id': 'FileSystemId',
        'file_system_name': 'FileSystemName',
        'project_name': 'ProjectName',
        'tags': 'Tags'
    }

    def __init__(self, auto_expand=None, auto_expand_limit=None, auto_expand_step=None, auto_expand_threshold=None, description=None, file_system_id=None, file_system_name=None, project_name=None, tags=None, _configuration=None):  # noqa: E501
        """UpdateFileSystemRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._auto_expand = None
        self._auto_expand_limit = None
        self._auto_expand_step = None
        self._auto_expand_threshold = None
        self._description = None
        self._file_system_id = None
        self._file_system_name = None
        self._project_name = None
        self._tags = None
        self.discriminator = None

        if auto_expand is not None:
            self.auto_expand = auto_expand
        if auto_expand_limit is not None:
            self.auto_expand_limit = auto_expand_limit
        if auto_expand_step is not None:
            self.auto_expand_step = auto_expand_step
        if auto_expand_threshold is not None:
            self.auto_expand_threshold = auto_expand_threshold
        if description is not None:
            self.description = description
        self.file_system_id = file_system_id
        if file_system_name is not None:
            self.file_system_name = file_system_name
        if project_name is not None:
            self.project_name = project_name
        if tags is not None:
            self.tags = tags

    @property
    def auto_expand(self):
        """Gets the auto_expand of this UpdateFileSystemRequest.  # noqa: E501


        :return: The auto_expand of this UpdateFileSystemRequest.  # noqa: E501
        :rtype: bool
        """
        return self._auto_expand

    @auto_expand.setter
    def auto_expand(self, auto_expand):
        """Sets the auto_expand of this UpdateFileSystemRequest.


        :param auto_expand: The auto_expand of this UpdateFileSystemRequest.  # noqa: E501
        :type: bool
        """

        self._auto_expand = auto_expand

    @property
    def auto_expand_limit(self):
        """Gets the auto_expand_limit of this UpdateFileSystemRequest.  # noqa: E501


        :return: The auto_expand_limit of this UpdateFileSystemRequest.  # noqa: E501
        :rtype: int
        """
        return self._auto_expand_limit

    @auto_expand_limit.setter
    def auto_expand_limit(self, auto_expand_limit):
        """Sets the auto_expand_limit of this UpdateFileSystemRequest.


        :param auto_expand_limit: The auto_expand_limit of this UpdateFileSystemRequest.  # noqa: E501
        :type: int
        """

        self._auto_expand_limit = auto_expand_limit

    @property
    def auto_expand_step(self):
        """Gets the auto_expand_step of this UpdateFileSystemRequest.  # noqa: E501


        :return: The auto_expand_step of this UpdateFileSystemRequest.  # noqa: E501
        :rtype: int
        """
        return self._auto_expand_step

    @auto_expand_step.setter
    def auto_expand_step(self, auto_expand_step):
        """Sets the auto_expand_step of this UpdateFileSystemRequest.


        :param auto_expand_step: The auto_expand_step of this UpdateFileSystemRequest.  # noqa: E501
        :type: int
        """

        self._auto_expand_step = auto_expand_step

    @property
    def auto_expand_threshold(self):
        """Gets the auto_expand_threshold of this UpdateFileSystemRequest.  # noqa: E501


        :return: The auto_expand_threshold of this UpdateFileSystemRequest.  # noqa: E501
        :rtype: int
        """
        return self._auto_expand_threshold

    @auto_expand_threshold.setter
    def auto_expand_threshold(self, auto_expand_threshold):
        """Sets the auto_expand_threshold of this UpdateFileSystemRequest.


        :param auto_expand_threshold: The auto_expand_threshold of this UpdateFileSystemRequest.  # noqa: E501
        :type: int
        """

        self._auto_expand_threshold = auto_expand_threshold

    @property
    def description(self):
        """Gets the description of this UpdateFileSystemRequest.  # noqa: E501


        :return: The description of this UpdateFileSystemRequest.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this UpdateFileSystemRequest.


        :param description: The description of this UpdateFileSystemRequest.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def file_system_id(self):
        """Gets the file_system_id of this UpdateFileSystemRequest.  # noqa: E501


        :return: The file_system_id of this UpdateFileSystemRequest.  # noqa: E501
        :rtype: str
        """
        return self._file_system_id

    @file_system_id.setter
    def file_system_id(self, file_system_id):
        """Sets the file_system_id of this UpdateFileSystemRequest.


        :param file_system_id: The file_system_id of this UpdateFileSystemRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and file_system_id is None:
            raise ValueError("Invalid value for `file_system_id`, must not be `None`")  # noqa: E501

        self._file_system_id = file_system_id

    @property
    def file_system_name(self):
        """Gets the file_system_name of this UpdateFileSystemRequest.  # noqa: E501


        :return: The file_system_name of this UpdateFileSystemRequest.  # noqa: E501
        :rtype: str
        """
        return self._file_system_name

    @file_system_name.setter
    def file_system_name(self, file_system_name):
        """Sets the file_system_name of this UpdateFileSystemRequest.


        :param file_system_name: The file_system_name of this UpdateFileSystemRequest.  # noqa: E501
        :type: str
        """

        self._file_system_name = file_system_name

    @property
    def project_name(self):
        """Gets the project_name of this UpdateFileSystemRequest.  # noqa: E501


        :return: The project_name of this UpdateFileSystemRequest.  # noqa: E501
        :rtype: str
        """
        return self._project_name

    @project_name.setter
    def project_name(self, project_name):
        """Sets the project_name of this UpdateFileSystemRequest.


        :param project_name: The project_name of this UpdateFileSystemRequest.  # noqa: E501
        :type: str
        """

        self._project_name = project_name

    @property
    def tags(self):
        """Gets the tags of this UpdateFileSystemRequest.  # noqa: E501


        :return: The tags of this UpdateFileSystemRequest.  # noqa: E501
        :rtype: list[TagForUpdateFileSystemInput]
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """Sets the tags of this UpdateFileSystemRequest.


        :param tags: The tags of this UpdateFileSystemRequest.  # noqa: E501
        :type: list[TagForUpdateFileSystemInput]
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
        if issubclass(UpdateFileSystemRequest, dict):
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
        if not isinstance(other, UpdateFileSystemRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UpdateFileSystemRequest):
            return True

        return self.to_dict() != other.to_dict()
