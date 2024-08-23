# coding: utf-8

"""
    vke

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class ItemForListKubeconfigsOutput(object):
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
        'cluster_id': 'str',
        'create_time': 'str',
        'expire_time': 'str',
        'id': 'str',
        'kubeconfig': 'str',
        'role_id': 'int',
        'type': 'str',
        'user_id': 'int'
    }

    attribute_map = {
        'cluster_id': 'ClusterId',
        'create_time': 'CreateTime',
        'expire_time': 'ExpireTime',
        'id': 'Id',
        'kubeconfig': 'Kubeconfig',
        'role_id': 'RoleId',
        'type': 'Type',
        'user_id': 'UserId'
    }

    def __init__(self, cluster_id=None, create_time=None, expire_time=None, id=None, kubeconfig=None, role_id=None, type=None, user_id=None, _configuration=None):  # noqa: E501
        """ItemForListKubeconfigsOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._cluster_id = None
        self._create_time = None
        self._expire_time = None
        self._id = None
        self._kubeconfig = None
        self._role_id = None
        self._type = None
        self._user_id = None
        self.discriminator = None

        if cluster_id is not None:
            self.cluster_id = cluster_id
        if create_time is not None:
            self.create_time = create_time
        if expire_time is not None:
            self.expire_time = expire_time
        if id is not None:
            self.id = id
        if kubeconfig is not None:
            self.kubeconfig = kubeconfig
        if role_id is not None:
            self.role_id = role_id
        if type is not None:
            self.type = type
        if user_id is not None:
            self.user_id = user_id

    @property
    def cluster_id(self):
        """Gets the cluster_id of this ItemForListKubeconfigsOutput.  # noqa: E501


        :return: The cluster_id of this ItemForListKubeconfigsOutput.  # noqa: E501
        :rtype: str
        """
        return self._cluster_id

    @cluster_id.setter
    def cluster_id(self, cluster_id):
        """Sets the cluster_id of this ItemForListKubeconfigsOutput.


        :param cluster_id: The cluster_id of this ItemForListKubeconfigsOutput.  # noqa: E501
        :type: str
        """

        self._cluster_id = cluster_id

    @property
    def create_time(self):
        """Gets the create_time of this ItemForListKubeconfigsOutput.  # noqa: E501


        :return: The create_time of this ItemForListKubeconfigsOutput.  # noqa: E501
        :rtype: str
        """
        return self._create_time

    @create_time.setter
    def create_time(self, create_time):
        """Sets the create_time of this ItemForListKubeconfigsOutput.


        :param create_time: The create_time of this ItemForListKubeconfigsOutput.  # noqa: E501
        :type: str
        """

        self._create_time = create_time

    @property
    def expire_time(self):
        """Gets the expire_time of this ItemForListKubeconfigsOutput.  # noqa: E501


        :return: The expire_time of this ItemForListKubeconfigsOutput.  # noqa: E501
        :rtype: str
        """
        return self._expire_time

    @expire_time.setter
    def expire_time(self, expire_time):
        """Sets the expire_time of this ItemForListKubeconfigsOutput.


        :param expire_time: The expire_time of this ItemForListKubeconfigsOutput.  # noqa: E501
        :type: str
        """

        self._expire_time = expire_time

    @property
    def id(self):
        """Gets the id of this ItemForListKubeconfigsOutput.  # noqa: E501


        :return: The id of this ItemForListKubeconfigsOutput.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this ItemForListKubeconfigsOutput.


        :param id: The id of this ItemForListKubeconfigsOutput.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def kubeconfig(self):
        """Gets the kubeconfig of this ItemForListKubeconfigsOutput.  # noqa: E501


        :return: The kubeconfig of this ItemForListKubeconfigsOutput.  # noqa: E501
        :rtype: str
        """
        return self._kubeconfig

    @kubeconfig.setter
    def kubeconfig(self, kubeconfig):
        """Sets the kubeconfig of this ItemForListKubeconfigsOutput.


        :param kubeconfig: The kubeconfig of this ItemForListKubeconfigsOutput.  # noqa: E501
        :type: str
        """

        self._kubeconfig = kubeconfig

    @property
    def role_id(self):
        """Gets the role_id of this ItemForListKubeconfigsOutput.  # noqa: E501


        :return: The role_id of this ItemForListKubeconfigsOutput.  # noqa: E501
        :rtype: int
        """
        return self._role_id

    @role_id.setter
    def role_id(self, role_id):
        """Sets the role_id of this ItemForListKubeconfigsOutput.


        :param role_id: The role_id of this ItemForListKubeconfigsOutput.  # noqa: E501
        :type: int
        """

        self._role_id = role_id

    @property
    def type(self):
        """Gets the type of this ItemForListKubeconfigsOutput.  # noqa: E501


        :return: The type of this ItemForListKubeconfigsOutput.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this ItemForListKubeconfigsOutput.


        :param type: The type of this ItemForListKubeconfigsOutput.  # noqa: E501
        :type: str
        """

        self._type = type

    @property
    def user_id(self):
        """Gets the user_id of this ItemForListKubeconfigsOutput.  # noqa: E501


        :return: The user_id of this ItemForListKubeconfigsOutput.  # noqa: E501
        :rtype: int
        """
        return self._user_id

    @user_id.setter
    def user_id(self, user_id):
        """Sets the user_id of this ItemForListKubeconfigsOutput.


        :param user_id: The user_id of this ItemForListKubeconfigsOutput.  # noqa: E501
        :type: int
        """

        self._user_id = user_id

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
        if issubclass(ItemForListKubeconfigsOutput, dict):
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
        if not isinstance(other, ItemForListKubeconfigsOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ItemForListKubeconfigsOutput):
            return True

        return self.to_dict() != other.to_dict()
