# coding: utf-8

"""
    dms

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class SourceForQueryDataMigrateTaskOutput(object):
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
        'object_source_config': 'ObjectSourceConfigForQueryDataMigrateTaskOutput',
        'url_source_config': 'UrlSourceConfigForQueryDataMigrateTaskOutput'
    }

    attribute_map = {
        'object_source_config': 'ObjectSourceConfig',
        'url_source_config': 'UrlSourceConfig'
    }

    def __init__(self, object_source_config=None, url_source_config=None, _configuration=None):  # noqa: E501
        """SourceForQueryDataMigrateTaskOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._object_source_config = None
        self._url_source_config = None
        self.discriminator = None

        if object_source_config is not None:
            self.object_source_config = object_source_config
        if url_source_config is not None:
            self.url_source_config = url_source_config

    @property
    def object_source_config(self):
        """Gets the object_source_config of this SourceForQueryDataMigrateTaskOutput.  # noqa: E501


        :return: The object_source_config of this SourceForQueryDataMigrateTaskOutput.  # noqa: E501
        :rtype: ObjectSourceConfigForQueryDataMigrateTaskOutput
        """
        return self._object_source_config

    @object_source_config.setter
    def object_source_config(self, object_source_config):
        """Sets the object_source_config of this SourceForQueryDataMigrateTaskOutput.


        :param object_source_config: The object_source_config of this SourceForQueryDataMigrateTaskOutput.  # noqa: E501
        :type: ObjectSourceConfigForQueryDataMigrateTaskOutput
        """

        self._object_source_config = object_source_config

    @property
    def url_source_config(self):
        """Gets the url_source_config of this SourceForQueryDataMigrateTaskOutput.  # noqa: E501


        :return: The url_source_config of this SourceForQueryDataMigrateTaskOutput.  # noqa: E501
        :rtype: UrlSourceConfigForQueryDataMigrateTaskOutput
        """
        return self._url_source_config

    @url_source_config.setter
    def url_source_config(self, url_source_config):
        """Sets the url_source_config of this SourceForQueryDataMigrateTaskOutput.


        :param url_source_config: The url_source_config of this SourceForQueryDataMigrateTaskOutput.  # noqa: E501
        :type: UrlSourceConfigForQueryDataMigrateTaskOutput
        """

        self._url_source_config = url_source_config

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
        if issubclass(SourceForQueryDataMigrateTaskOutput, dict):
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
        if not isinstance(other, SourceForQueryDataMigrateTaskOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SourceForQueryDataMigrateTaskOutput):
            return True

        return self.to_dict() != other.to_dict()
