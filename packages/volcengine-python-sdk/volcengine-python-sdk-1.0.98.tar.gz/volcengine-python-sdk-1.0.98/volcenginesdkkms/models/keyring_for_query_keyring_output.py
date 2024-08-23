# coding: utf-8

"""
    kms

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class KeyringForQueryKeyringOutput(object):
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
        'creation_date': 'int',
        'description': 'str',
        'id': 'str',
        'keyring_name': 'str',
        'keyring_type': 'str',
        'project_name': 'str',
        'uid': 'str',
        'update_date': 'int'
    }

    attribute_map = {
        'creation_date': 'CreationDate',
        'description': 'Description',
        'id': 'ID',
        'keyring_name': 'KeyringName',
        'keyring_type': 'KeyringType',
        'project_name': 'ProjectName',
        'uid': 'UID',
        'update_date': 'UpdateDate'
    }

    def __init__(self, creation_date=None, description=None, id=None, keyring_name=None, keyring_type=None, project_name=None, uid=None, update_date=None, _configuration=None):  # noqa: E501
        """KeyringForQueryKeyringOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._creation_date = None
        self._description = None
        self._id = None
        self._keyring_name = None
        self._keyring_type = None
        self._project_name = None
        self._uid = None
        self._update_date = None
        self.discriminator = None

        if creation_date is not None:
            self.creation_date = creation_date
        if description is not None:
            self.description = description
        if id is not None:
            self.id = id
        if keyring_name is not None:
            self.keyring_name = keyring_name
        if keyring_type is not None:
            self.keyring_type = keyring_type
        if project_name is not None:
            self.project_name = project_name
        if uid is not None:
            self.uid = uid
        if update_date is not None:
            self.update_date = update_date

    @property
    def creation_date(self):
        """Gets the creation_date of this KeyringForQueryKeyringOutput.  # noqa: E501


        :return: The creation_date of this KeyringForQueryKeyringOutput.  # noqa: E501
        :rtype: int
        """
        return self._creation_date

    @creation_date.setter
    def creation_date(self, creation_date):
        """Sets the creation_date of this KeyringForQueryKeyringOutput.


        :param creation_date: The creation_date of this KeyringForQueryKeyringOutput.  # noqa: E501
        :type: int
        """

        self._creation_date = creation_date

    @property
    def description(self):
        """Gets the description of this KeyringForQueryKeyringOutput.  # noqa: E501


        :return: The description of this KeyringForQueryKeyringOutput.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this KeyringForQueryKeyringOutput.


        :param description: The description of this KeyringForQueryKeyringOutput.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def id(self):
        """Gets the id of this KeyringForQueryKeyringOutput.  # noqa: E501


        :return: The id of this KeyringForQueryKeyringOutput.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this KeyringForQueryKeyringOutput.


        :param id: The id of this KeyringForQueryKeyringOutput.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def keyring_name(self):
        """Gets the keyring_name of this KeyringForQueryKeyringOutput.  # noqa: E501


        :return: The keyring_name of this KeyringForQueryKeyringOutput.  # noqa: E501
        :rtype: str
        """
        return self._keyring_name

    @keyring_name.setter
    def keyring_name(self, keyring_name):
        """Sets the keyring_name of this KeyringForQueryKeyringOutput.


        :param keyring_name: The keyring_name of this KeyringForQueryKeyringOutput.  # noqa: E501
        :type: str
        """

        self._keyring_name = keyring_name

    @property
    def keyring_type(self):
        """Gets the keyring_type of this KeyringForQueryKeyringOutput.  # noqa: E501


        :return: The keyring_type of this KeyringForQueryKeyringOutput.  # noqa: E501
        :rtype: str
        """
        return self._keyring_type

    @keyring_type.setter
    def keyring_type(self, keyring_type):
        """Sets the keyring_type of this KeyringForQueryKeyringOutput.


        :param keyring_type: The keyring_type of this KeyringForQueryKeyringOutput.  # noqa: E501
        :type: str
        """

        self._keyring_type = keyring_type

    @property
    def project_name(self):
        """Gets the project_name of this KeyringForQueryKeyringOutput.  # noqa: E501


        :return: The project_name of this KeyringForQueryKeyringOutput.  # noqa: E501
        :rtype: str
        """
        return self._project_name

    @project_name.setter
    def project_name(self, project_name):
        """Sets the project_name of this KeyringForQueryKeyringOutput.


        :param project_name: The project_name of this KeyringForQueryKeyringOutput.  # noqa: E501
        :type: str
        """

        self._project_name = project_name

    @property
    def uid(self):
        """Gets the uid of this KeyringForQueryKeyringOutput.  # noqa: E501


        :return: The uid of this KeyringForQueryKeyringOutput.  # noqa: E501
        :rtype: str
        """
        return self._uid

    @uid.setter
    def uid(self, uid):
        """Sets the uid of this KeyringForQueryKeyringOutput.


        :param uid: The uid of this KeyringForQueryKeyringOutput.  # noqa: E501
        :type: str
        """

        self._uid = uid

    @property
    def update_date(self):
        """Gets the update_date of this KeyringForQueryKeyringOutput.  # noqa: E501


        :return: The update_date of this KeyringForQueryKeyringOutput.  # noqa: E501
        :rtype: int
        """
        return self._update_date

    @update_date.setter
    def update_date(self, update_date):
        """Sets the update_date of this KeyringForQueryKeyringOutput.


        :param update_date: The update_date of this KeyringForQueryKeyringOutput.  # noqa: E501
        :type: int
        """

        self._update_date = update_date

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
        if issubclass(KeyringForQueryKeyringOutput, dict):
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
        if not isinstance(other, KeyringForQueryKeyringOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, KeyringForQueryKeyringOutput):
            return True

        return self.to_dict() != other.to_dict()
