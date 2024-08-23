# coding: utf-8

"""
    waf

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class CheckLLMPromptRequest(object):
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
        'content': 'str',
        'content_type': 'int',
        'host': 'str',
        'msg_class': 'int',
        'region': 'str'
    }

    attribute_map = {
        'content': 'Content',
        'content_type': 'ContentType',
        'host': 'Host',
        'msg_class': 'MsgClass',
        'region': 'Region'
    }

    def __init__(self, content=None, content_type=None, host=None, msg_class=None, region=None, _configuration=None):  # noqa: E501
        """CheckLLMPromptRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._content = None
        self._content_type = None
        self._host = None
        self._msg_class = None
        self._region = None
        self.discriminator = None

        self.content = content
        self.content_type = content_type
        self.host = host
        if msg_class is not None:
            self.msg_class = msg_class
        self.region = region

    @property
    def content(self):
        """Gets the content of this CheckLLMPromptRequest.  # noqa: E501


        :return: The content of this CheckLLMPromptRequest.  # noqa: E501
        :rtype: str
        """
        return self._content

    @content.setter
    def content(self, content):
        """Sets the content of this CheckLLMPromptRequest.


        :param content: The content of this CheckLLMPromptRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and content is None:
            raise ValueError("Invalid value for `content`, must not be `None`")  # noqa: E501

        self._content = content

    @property
    def content_type(self):
        """Gets the content_type of this CheckLLMPromptRequest.  # noqa: E501


        :return: The content_type of this CheckLLMPromptRequest.  # noqa: E501
        :rtype: int
        """
        return self._content_type

    @content_type.setter
    def content_type(self, content_type):
        """Sets the content_type of this CheckLLMPromptRequest.


        :param content_type: The content_type of this CheckLLMPromptRequest.  # noqa: E501
        :type: int
        """
        if self._configuration.client_side_validation and content_type is None:
            raise ValueError("Invalid value for `content_type`, must not be `None`")  # noqa: E501

        self._content_type = content_type

    @property
    def host(self):
        """Gets the host of this CheckLLMPromptRequest.  # noqa: E501


        :return: The host of this CheckLLMPromptRequest.  # noqa: E501
        :rtype: str
        """
        return self._host

    @host.setter
    def host(self, host):
        """Sets the host of this CheckLLMPromptRequest.


        :param host: The host of this CheckLLMPromptRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and host is None:
            raise ValueError("Invalid value for `host`, must not be `None`")  # noqa: E501

        self._host = host

    @property
    def msg_class(self):
        """Gets the msg_class of this CheckLLMPromptRequest.  # noqa: E501


        :return: The msg_class of this CheckLLMPromptRequest.  # noqa: E501
        :rtype: int
        """
        return self._msg_class

    @msg_class.setter
    def msg_class(self, msg_class):
        """Sets the msg_class of this CheckLLMPromptRequest.


        :param msg_class: The msg_class of this CheckLLMPromptRequest.  # noqa: E501
        :type: int
        """

        self._msg_class = msg_class

    @property
    def region(self):
        """Gets the region of this CheckLLMPromptRequest.  # noqa: E501


        :return: The region of this CheckLLMPromptRequest.  # noqa: E501
        :rtype: str
        """
        return self._region

    @region.setter
    def region(self, region):
        """Sets the region of this CheckLLMPromptRequest.


        :param region: The region of this CheckLLMPromptRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and region is None:
            raise ValueError("Invalid value for `region`, must not be `None`")  # noqa: E501

        self._region = region

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
        if issubclass(CheckLLMPromptRequest, dict):
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
        if not isinstance(other, CheckLLMPromptRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CheckLLMPromptRequest):
            return True

        return self.to_dict() != other.to_dict()
