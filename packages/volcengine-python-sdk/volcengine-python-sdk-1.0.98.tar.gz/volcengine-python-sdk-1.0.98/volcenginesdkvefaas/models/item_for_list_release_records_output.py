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


class ItemForListReleaseRecordsOutput(object):
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
        'finish_time': 'str',
        'function_id': 'str',
        'id': 'str',
        'last_update_time': 'str',
        'source_revision_number': 'int',
        'status': 'str',
        'target_revision_number': 'int'
    }

    attribute_map = {
        'creation_time': 'CreationTime',
        'description': 'Description',
        'finish_time': 'FinishTime',
        'function_id': 'FunctionId',
        'id': 'Id',
        'last_update_time': 'LastUpdateTime',
        'source_revision_number': 'SourceRevisionNumber',
        'status': 'Status',
        'target_revision_number': 'TargetRevisionNumber'
    }

    def __init__(self, creation_time=None, description=None, finish_time=None, function_id=None, id=None, last_update_time=None, source_revision_number=None, status=None, target_revision_number=None, _configuration=None):  # noqa: E501
        """ItemForListReleaseRecordsOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._creation_time = None
        self._description = None
        self._finish_time = None
        self._function_id = None
        self._id = None
        self._last_update_time = None
        self._source_revision_number = None
        self._status = None
        self._target_revision_number = None
        self.discriminator = None

        if creation_time is not None:
            self.creation_time = creation_time
        if description is not None:
            self.description = description
        if finish_time is not None:
            self.finish_time = finish_time
        if function_id is not None:
            self.function_id = function_id
        if id is not None:
            self.id = id
        if last_update_time is not None:
            self.last_update_time = last_update_time
        if source_revision_number is not None:
            self.source_revision_number = source_revision_number
        if status is not None:
            self.status = status
        if target_revision_number is not None:
            self.target_revision_number = target_revision_number

    @property
    def creation_time(self):
        """Gets the creation_time of this ItemForListReleaseRecordsOutput.  # noqa: E501


        :return: The creation_time of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :rtype: str
        """
        return self._creation_time

    @creation_time.setter
    def creation_time(self, creation_time):
        """Sets the creation_time of this ItemForListReleaseRecordsOutput.


        :param creation_time: The creation_time of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :type: str
        """

        self._creation_time = creation_time

    @property
    def description(self):
        """Gets the description of this ItemForListReleaseRecordsOutput.  # noqa: E501


        :return: The description of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this ItemForListReleaseRecordsOutput.


        :param description: The description of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def finish_time(self):
        """Gets the finish_time of this ItemForListReleaseRecordsOutput.  # noqa: E501


        :return: The finish_time of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :rtype: str
        """
        return self._finish_time

    @finish_time.setter
    def finish_time(self, finish_time):
        """Sets the finish_time of this ItemForListReleaseRecordsOutput.


        :param finish_time: The finish_time of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :type: str
        """

        self._finish_time = finish_time

    @property
    def function_id(self):
        """Gets the function_id of this ItemForListReleaseRecordsOutput.  # noqa: E501


        :return: The function_id of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :rtype: str
        """
        return self._function_id

    @function_id.setter
    def function_id(self, function_id):
        """Sets the function_id of this ItemForListReleaseRecordsOutput.


        :param function_id: The function_id of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :type: str
        """

        self._function_id = function_id

    @property
    def id(self):
        """Gets the id of this ItemForListReleaseRecordsOutput.  # noqa: E501


        :return: The id of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this ItemForListReleaseRecordsOutput.


        :param id: The id of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def last_update_time(self):
        """Gets the last_update_time of this ItemForListReleaseRecordsOutput.  # noqa: E501


        :return: The last_update_time of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :rtype: str
        """
        return self._last_update_time

    @last_update_time.setter
    def last_update_time(self, last_update_time):
        """Sets the last_update_time of this ItemForListReleaseRecordsOutput.


        :param last_update_time: The last_update_time of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :type: str
        """

        self._last_update_time = last_update_time

    @property
    def source_revision_number(self):
        """Gets the source_revision_number of this ItemForListReleaseRecordsOutput.  # noqa: E501


        :return: The source_revision_number of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :rtype: int
        """
        return self._source_revision_number

    @source_revision_number.setter
    def source_revision_number(self, source_revision_number):
        """Sets the source_revision_number of this ItemForListReleaseRecordsOutput.


        :param source_revision_number: The source_revision_number of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :type: int
        """

        self._source_revision_number = source_revision_number

    @property
    def status(self):
        """Gets the status of this ItemForListReleaseRecordsOutput.  # noqa: E501


        :return: The status of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this ItemForListReleaseRecordsOutput.


        :param status: The status of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def target_revision_number(self):
        """Gets the target_revision_number of this ItemForListReleaseRecordsOutput.  # noqa: E501


        :return: The target_revision_number of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :rtype: int
        """
        return self._target_revision_number

    @target_revision_number.setter
    def target_revision_number(self, target_revision_number):
        """Sets the target_revision_number of this ItemForListReleaseRecordsOutput.


        :param target_revision_number: The target_revision_number of this ItemForListReleaseRecordsOutput.  # noqa: E501
        :type: int
        """

        self._target_revision_number = target_revision_number

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
        if issubclass(ItemForListReleaseRecordsOutput, dict):
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
        if not isinstance(other, ItemForListReleaseRecordsOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ItemForListReleaseRecordsOutput):
            return True

        return self.to_dict() != other.to_dict()
