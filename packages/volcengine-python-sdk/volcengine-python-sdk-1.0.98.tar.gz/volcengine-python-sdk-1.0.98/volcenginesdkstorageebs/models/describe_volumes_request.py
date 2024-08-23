# coding: utf-8

"""
    storage_ebs

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class DescribeVolumesRequest(object):
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
        'instance_id': 'str',
        'kind': 'str',
        'page_number': 'int',
        'page_size': 'int',
        'project_name': 'str',
        'tag_filters': 'list[TagFilterForDescribeVolumesInput]',
        'volume_ids': 'list[str]',
        'volume_name': 'str',
        'volume_status': 'str',
        'volume_type': 'str',
        'zone_id': 'str'
    }

    attribute_map = {
        'instance_id': 'InstanceId',
        'kind': 'Kind',
        'page_number': 'PageNumber',
        'page_size': 'PageSize',
        'project_name': 'ProjectName',
        'tag_filters': 'TagFilters',
        'volume_ids': 'VolumeIds',
        'volume_name': 'VolumeName',
        'volume_status': 'VolumeStatus',
        'volume_type': 'VolumeType',
        'zone_id': 'ZoneId'
    }

    def __init__(self, instance_id=None, kind=None, page_number=None, page_size=None, project_name=None, tag_filters=None, volume_ids=None, volume_name=None, volume_status=None, volume_type=None, zone_id=None, _configuration=None):  # noqa: E501
        """DescribeVolumesRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._instance_id = None
        self._kind = None
        self._page_number = None
        self._page_size = None
        self._project_name = None
        self._tag_filters = None
        self._volume_ids = None
        self._volume_name = None
        self._volume_status = None
        self._volume_type = None
        self._zone_id = None
        self.discriminator = None

        if instance_id is not None:
            self.instance_id = instance_id
        if kind is not None:
            self.kind = kind
        if page_number is not None:
            self.page_number = page_number
        if page_size is not None:
            self.page_size = page_size
        if project_name is not None:
            self.project_name = project_name
        if tag_filters is not None:
            self.tag_filters = tag_filters
        if volume_ids is not None:
            self.volume_ids = volume_ids
        if volume_name is not None:
            self.volume_name = volume_name
        if volume_status is not None:
            self.volume_status = volume_status
        if volume_type is not None:
            self.volume_type = volume_type
        if zone_id is not None:
            self.zone_id = zone_id

    @property
    def instance_id(self):
        """Gets the instance_id of this DescribeVolumesRequest.  # noqa: E501


        :return: The instance_id of this DescribeVolumesRequest.  # noqa: E501
        :rtype: str
        """
        return self._instance_id

    @instance_id.setter
    def instance_id(self, instance_id):
        """Sets the instance_id of this DescribeVolumesRequest.


        :param instance_id: The instance_id of this DescribeVolumesRequest.  # noqa: E501
        :type: str
        """

        self._instance_id = instance_id

    @property
    def kind(self):
        """Gets the kind of this DescribeVolumesRequest.  # noqa: E501


        :return: The kind of this DescribeVolumesRequest.  # noqa: E501
        :rtype: str
        """
        return self._kind

    @kind.setter
    def kind(self, kind):
        """Sets the kind of this DescribeVolumesRequest.


        :param kind: The kind of this DescribeVolumesRequest.  # noqa: E501
        :type: str
        """

        self._kind = kind

    @property
    def page_number(self):
        """Gets the page_number of this DescribeVolumesRequest.  # noqa: E501


        :return: The page_number of this DescribeVolumesRequest.  # noqa: E501
        :rtype: int
        """
        return self._page_number

    @page_number.setter
    def page_number(self, page_number):
        """Sets the page_number of this DescribeVolumesRequest.


        :param page_number: The page_number of this DescribeVolumesRequest.  # noqa: E501
        :type: int
        """

        self._page_number = page_number

    @property
    def page_size(self):
        """Gets the page_size of this DescribeVolumesRequest.  # noqa: E501


        :return: The page_size of this DescribeVolumesRequest.  # noqa: E501
        :rtype: int
        """
        return self._page_size

    @page_size.setter
    def page_size(self, page_size):
        """Sets the page_size of this DescribeVolumesRequest.


        :param page_size: The page_size of this DescribeVolumesRequest.  # noqa: E501
        :type: int
        """

        self._page_size = page_size

    @property
    def project_name(self):
        """Gets the project_name of this DescribeVolumesRequest.  # noqa: E501


        :return: The project_name of this DescribeVolumesRequest.  # noqa: E501
        :rtype: str
        """
        return self._project_name

    @project_name.setter
    def project_name(self, project_name):
        """Sets the project_name of this DescribeVolumesRequest.


        :param project_name: The project_name of this DescribeVolumesRequest.  # noqa: E501
        :type: str
        """

        self._project_name = project_name

    @property
    def tag_filters(self):
        """Gets the tag_filters of this DescribeVolumesRequest.  # noqa: E501


        :return: The tag_filters of this DescribeVolumesRequest.  # noqa: E501
        :rtype: list[TagFilterForDescribeVolumesInput]
        """
        return self._tag_filters

    @tag_filters.setter
    def tag_filters(self, tag_filters):
        """Sets the tag_filters of this DescribeVolumesRequest.


        :param tag_filters: The tag_filters of this DescribeVolumesRequest.  # noqa: E501
        :type: list[TagFilterForDescribeVolumesInput]
        """

        self._tag_filters = tag_filters

    @property
    def volume_ids(self):
        """Gets the volume_ids of this DescribeVolumesRequest.  # noqa: E501


        :return: The volume_ids of this DescribeVolumesRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._volume_ids

    @volume_ids.setter
    def volume_ids(self, volume_ids):
        """Sets the volume_ids of this DescribeVolumesRequest.


        :param volume_ids: The volume_ids of this DescribeVolumesRequest.  # noqa: E501
        :type: list[str]
        """

        self._volume_ids = volume_ids

    @property
    def volume_name(self):
        """Gets the volume_name of this DescribeVolumesRequest.  # noqa: E501


        :return: The volume_name of this DescribeVolumesRequest.  # noqa: E501
        :rtype: str
        """
        return self._volume_name

    @volume_name.setter
    def volume_name(self, volume_name):
        """Sets the volume_name of this DescribeVolumesRequest.


        :param volume_name: The volume_name of this DescribeVolumesRequest.  # noqa: E501
        :type: str
        """

        self._volume_name = volume_name

    @property
    def volume_status(self):
        """Gets the volume_status of this DescribeVolumesRequest.  # noqa: E501


        :return: The volume_status of this DescribeVolumesRequest.  # noqa: E501
        :rtype: str
        """
        return self._volume_status

    @volume_status.setter
    def volume_status(self, volume_status):
        """Sets the volume_status of this DescribeVolumesRequest.


        :param volume_status: The volume_status of this DescribeVolumesRequest.  # noqa: E501
        :type: str
        """

        self._volume_status = volume_status

    @property
    def volume_type(self):
        """Gets the volume_type of this DescribeVolumesRequest.  # noqa: E501


        :return: The volume_type of this DescribeVolumesRequest.  # noqa: E501
        :rtype: str
        """
        return self._volume_type

    @volume_type.setter
    def volume_type(self, volume_type):
        """Sets the volume_type of this DescribeVolumesRequest.


        :param volume_type: The volume_type of this DescribeVolumesRequest.  # noqa: E501
        :type: str
        """

        self._volume_type = volume_type

    @property
    def zone_id(self):
        """Gets the zone_id of this DescribeVolumesRequest.  # noqa: E501


        :return: The zone_id of this DescribeVolumesRequest.  # noqa: E501
        :rtype: str
        """
        return self._zone_id

    @zone_id.setter
    def zone_id(self, zone_id):
        """Sets the zone_id of this DescribeVolumesRequest.


        :param zone_id: The zone_id of this DescribeVolumesRequest.  # noqa: E501
        :type: str
        """

        self._zone_id = zone_id

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
        if issubclass(DescribeVolumesRequest, dict):
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
        if not isinstance(other, DescribeVolumesRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DescribeVolumesRequest):
            return True

        return self.to_dict() != other.to_dict()
