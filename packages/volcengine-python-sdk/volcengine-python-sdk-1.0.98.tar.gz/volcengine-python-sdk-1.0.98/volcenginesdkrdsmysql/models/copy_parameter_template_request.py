# coding: utf-8

"""
    rds_mysql

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class CopyParameterTemplateRequest(object):
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
        'src_template_id': 'str',
        'template_desc': 'str',
        'template_name': 'str'
    }

    attribute_map = {
        'src_template_id': 'SrcTemplateId',
        'template_desc': 'TemplateDesc',
        'template_name': 'TemplateName'
    }

    def __init__(self, src_template_id=None, template_desc=None, template_name=None, _configuration=None):  # noqa: E501
        """CopyParameterTemplateRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._src_template_id = None
        self._template_desc = None
        self._template_name = None
        self.discriminator = None

        self.src_template_id = src_template_id
        if template_desc is not None:
            self.template_desc = template_desc
        if template_name is not None:
            self.template_name = template_name

    @property
    def src_template_id(self):
        """Gets the src_template_id of this CopyParameterTemplateRequest.  # noqa: E501


        :return: The src_template_id of this CopyParameterTemplateRequest.  # noqa: E501
        :rtype: str
        """
        return self._src_template_id

    @src_template_id.setter
    def src_template_id(self, src_template_id):
        """Sets the src_template_id of this CopyParameterTemplateRequest.


        :param src_template_id: The src_template_id of this CopyParameterTemplateRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and src_template_id is None:
            raise ValueError("Invalid value for `src_template_id`, must not be `None`")  # noqa: E501

        self._src_template_id = src_template_id

    @property
    def template_desc(self):
        """Gets the template_desc of this CopyParameterTemplateRequest.  # noqa: E501


        :return: The template_desc of this CopyParameterTemplateRequest.  # noqa: E501
        :rtype: str
        """
        return self._template_desc

    @template_desc.setter
    def template_desc(self, template_desc):
        """Sets the template_desc of this CopyParameterTemplateRequest.


        :param template_desc: The template_desc of this CopyParameterTemplateRequest.  # noqa: E501
        :type: str
        """
        if (self._configuration.client_side_validation and
                template_desc is not None and len(template_desc) > 200):
            raise ValueError("Invalid value for `template_desc`, length must be less than or equal to `200`")  # noqa: E501

        self._template_desc = template_desc

    @property
    def template_name(self):
        """Gets the template_name of this CopyParameterTemplateRequest.  # noqa: E501


        :return: The template_name of this CopyParameterTemplateRequest.  # noqa: E501
        :rtype: str
        """
        return self._template_name

    @template_name.setter
    def template_name(self, template_name):
        """Sets the template_name of this CopyParameterTemplateRequest.


        :param template_name: The template_name of this CopyParameterTemplateRequest.  # noqa: E501
        :type: str
        """
        if (self._configuration.client_side_validation and
                template_name is not None and len(template_name) > 64):
            raise ValueError("Invalid value for `template_name`, length must be less than or equal to `64`")  # noqa: E501
        if (self._configuration.client_side_validation and
                template_name is not None and len(template_name) < 2):
            raise ValueError("Invalid value for `template_name`, length must be greater than or equal to `2`")  # noqa: E501

        self._template_name = template_name

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
        if issubclass(CopyParameterTemplateRequest, dict):
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
        if not isinstance(other, CopyParameterTemplateRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CopyParameterTemplateRequest):
            return True

        return self.to_dict() != other.to_dict()
