# coding: utf-8

"""
    vefaas

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class NasConfigForListFunctionsOutput(object):
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
        'file_system_id': 'str',
        'gid': 'int',
        'local_mount_path': 'str',
        'mount_point_id': 'str',
        'remote_path': 'str',
        'uid': 'int'
    }

    attribute_map = {
        'file_system_id': 'FileSystemId',
        'gid': 'Gid',
        'local_mount_path': 'LocalMountPath',
        'mount_point_id': 'MountPointId',
        'remote_path': 'RemotePath',
        'uid': 'Uid'
    }

    def __init__(self, file_system_id=None, gid=None, local_mount_path=None, mount_point_id=None, remote_path=None, uid=None, _configuration=None):  # noqa: E501
        """NasConfigForListFunctionsOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._file_system_id = None
        self._gid = None
        self._local_mount_path = None
        self._mount_point_id = None
        self._remote_path = None
        self._uid = None
        self.discriminator = None

        if file_system_id is not None:
            self.file_system_id = file_system_id
        if gid is not None:
            self.gid = gid
        if local_mount_path is not None:
            self.local_mount_path = local_mount_path
        if mount_point_id is not None:
            self.mount_point_id = mount_point_id
        if remote_path is not None:
            self.remote_path = remote_path
        if uid is not None:
            self.uid = uid

    @property
    def file_system_id(self):
        """Gets the file_system_id of this NasConfigForListFunctionsOutput.  # noqa: E501


        :return: The file_system_id of this NasConfigForListFunctionsOutput.  # noqa: E501
        :rtype: str
        """
        return self._file_system_id

    @file_system_id.setter
    def file_system_id(self, file_system_id):
        """Sets the file_system_id of this NasConfigForListFunctionsOutput.


        :param file_system_id: The file_system_id of this NasConfigForListFunctionsOutput.  # noqa: E501
        :type: str
        """

        self._file_system_id = file_system_id

    @property
    def gid(self):
        """Gets the gid of this NasConfigForListFunctionsOutput.  # noqa: E501


        :return: The gid of this NasConfigForListFunctionsOutput.  # noqa: E501
        :rtype: int
        """
        return self._gid

    @gid.setter
    def gid(self, gid):
        """Sets the gid of this NasConfigForListFunctionsOutput.


        :param gid: The gid of this NasConfigForListFunctionsOutput.  # noqa: E501
        :type: int
        """

        self._gid = gid

    @property
    def local_mount_path(self):
        """Gets the local_mount_path of this NasConfigForListFunctionsOutput.  # noqa: E501


        :return: The local_mount_path of this NasConfigForListFunctionsOutput.  # noqa: E501
        :rtype: str
        """
        return self._local_mount_path

    @local_mount_path.setter
    def local_mount_path(self, local_mount_path):
        """Sets the local_mount_path of this NasConfigForListFunctionsOutput.


        :param local_mount_path: The local_mount_path of this NasConfigForListFunctionsOutput.  # noqa: E501
        :type: str
        """

        self._local_mount_path = local_mount_path

    @property
    def mount_point_id(self):
        """Gets the mount_point_id of this NasConfigForListFunctionsOutput.  # noqa: E501


        :return: The mount_point_id of this NasConfigForListFunctionsOutput.  # noqa: E501
        :rtype: str
        """
        return self._mount_point_id

    @mount_point_id.setter
    def mount_point_id(self, mount_point_id):
        """Sets the mount_point_id of this NasConfigForListFunctionsOutput.


        :param mount_point_id: The mount_point_id of this NasConfigForListFunctionsOutput.  # noqa: E501
        :type: str
        """

        self._mount_point_id = mount_point_id

    @property
    def remote_path(self):
        """Gets the remote_path of this NasConfigForListFunctionsOutput.  # noqa: E501


        :return: The remote_path of this NasConfigForListFunctionsOutput.  # noqa: E501
        :rtype: str
        """
        return self._remote_path

    @remote_path.setter
    def remote_path(self, remote_path):
        """Sets the remote_path of this NasConfigForListFunctionsOutput.


        :param remote_path: The remote_path of this NasConfigForListFunctionsOutput.  # noqa: E501
        :type: str
        """

        self._remote_path = remote_path

    @property
    def uid(self):
        """Gets the uid of this NasConfigForListFunctionsOutput.  # noqa: E501


        :return: The uid of this NasConfigForListFunctionsOutput.  # noqa: E501
        :rtype: int
        """
        return self._uid

    @uid.setter
    def uid(self, uid):
        """Sets the uid of this NasConfigForListFunctionsOutput.


        :param uid: The uid of this NasConfigForListFunctionsOutput.  # noqa: E501
        :type: int
        """

        self._uid = uid

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
        if issubclass(NasConfigForListFunctionsOutput, dict):
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
        if not isinstance(other, NasConfigForListFunctionsOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, NasConfigForListFunctionsOutput):
            return True

        return self.to_dict() != other.to_dict()
