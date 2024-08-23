# coding: utf-8

"""
    volc_observe

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class TLSTargetForListEventRulesOutput(object):
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
        'project_id': 'str',
        'project_name': 'str',
        'region_name_cn': 'str',
        'region_name_en': 'str',
        'topic_id': 'str'
    }

    attribute_map = {
        'project_id': 'ProjectId',
        'project_name': 'ProjectName',
        'region_name_cn': 'RegionNameCN',
        'region_name_en': 'RegionNameEN',
        'topic_id': 'TopicId'
    }

    def __init__(self, project_id=None, project_name=None, region_name_cn=None, region_name_en=None, topic_id=None, _configuration=None):  # noqa: E501
        """TLSTargetForListEventRulesOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._project_id = None
        self._project_name = None
        self._region_name_cn = None
        self._region_name_en = None
        self._topic_id = None
        self.discriminator = None

        if project_id is not None:
            self.project_id = project_id
        if project_name is not None:
            self.project_name = project_name
        if region_name_cn is not None:
            self.region_name_cn = region_name_cn
        if region_name_en is not None:
            self.region_name_en = region_name_en
        if topic_id is not None:
            self.topic_id = topic_id

    @property
    def project_id(self):
        """Gets the project_id of this TLSTargetForListEventRulesOutput.  # noqa: E501


        :return: The project_id of this TLSTargetForListEventRulesOutput.  # noqa: E501
        :rtype: str
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id):
        """Sets the project_id of this TLSTargetForListEventRulesOutput.


        :param project_id: The project_id of this TLSTargetForListEventRulesOutput.  # noqa: E501
        :type: str
        """

        self._project_id = project_id

    @property
    def project_name(self):
        """Gets the project_name of this TLSTargetForListEventRulesOutput.  # noqa: E501


        :return: The project_name of this TLSTargetForListEventRulesOutput.  # noqa: E501
        :rtype: str
        """
        return self._project_name

    @project_name.setter
    def project_name(self, project_name):
        """Sets the project_name of this TLSTargetForListEventRulesOutput.


        :param project_name: The project_name of this TLSTargetForListEventRulesOutput.  # noqa: E501
        :type: str
        """

        self._project_name = project_name

    @property
    def region_name_cn(self):
        """Gets the region_name_cn of this TLSTargetForListEventRulesOutput.  # noqa: E501


        :return: The region_name_cn of this TLSTargetForListEventRulesOutput.  # noqa: E501
        :rtype: str
        """
        return self._region_name_cn

    @region_name_cn.setter
    def region_name_cn(self, region_name_cn):
        """Sets the region_name_cn of this TLSTargetForListEventRulesOutput.


        :param region_name_cn: The region_name_cn of this TLSTargetForListEventRulesOutput.  # noqa: E501
        :type: str
        """

        self._region_name_cn = region_name_cn

    @property
    def region_name_en(self):
        """Gets the region_name_en of this TLSTargetForListEventRulesOutput.  # noqa: E501


        :return: The region_name_en of this TLSTargetForListEventRulesOutput.  # noqa: E501
        :rtype: str
        """
        return self._region_name_en

    @region_name_en.setter
    def region_name_en(self, region_name_en):
        """Sets the region_name_en of this TLSTargetForListEventRulesOutput.


        :param region_name_en: The region_name_en of this TLSTargetForListEventRulesOutput.  # noqa: E501
        :type: str
        """

        self._region_name_en = region_name_en

    @property
    def topic_id(self):
        """Gets the topic_id of this TLSTargetForListEventRulesOutput.  # noqa: E501


        :return: The topic_id of this TLSTargetForListEventRulesOutput.  # noqa: E501
        :rtype: str
        """
        return self._topic_id

    @topic_id.setter
    def topic_id(self, topic_id):
        """Sets the topic_id of this TLSTargetForListEventRulesOutput.


        :param topic_id: The topic_id of this TLSTargetForListEventRulesOutput.  # noqa: E501
        :type: str
        """

        self._topic_id = topic_id

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
        if issubclass(TLSTargetForListEventRulesOutput, dict):
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
        if not isinstance(other, TLSTargetForListEventRulesOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TLSTargetForListEventRulesOutput):
            return True

        return self.to_dict() != other.to_dict()
