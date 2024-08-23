# coding: utf-8

"""
    alb

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class RedirectConfigForCreateRulesInput(object):
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
        'redirect_domain': 'str',
        'redirect_http_code': 'str',
        'redirect_port': 'str',
        'redirect_protocol': 'str',
        'redirect_uri': 'str'
    }

    attribute_map = {
        'redirect_domain': 'RedirectDomain',
        'redirect_http_code': 'RedirectHttpCode',
        'redirect_port': 'RedirectPort',
        'redirect_protocol': 'RedirectProtocol',
        'redirect_uri': 'RedirectUri'
    }

    def __init__(self, redirect_domain=None, redirect_http_code=None, redirect_port=None, redirect_protocol=None, redirect_uri=None, _configuration=None):  # noqa: E501
        """RedirectConfigForCreateRulesInput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._redirect_domain = None
        self._redirect_http_code = None
        self._redirect_port = None
        self._redirect_protocol = None
        self._redirect_uri = None
        self.discriminator = None

        if redirect_domain is not None:
            self.redirect_domain = redirect_domain
        if redirect_http_code is not None:
            self.redirect_http_code = redirect_http_code
        if redirect_port is not None:
            self.redirect_port = redirect_port
        if redirect_protocol is not None:
            self.redirect_protocol = redirect_protocol
        if redirect_uri is not None:
            self.redirect_uri = redirect_uri

    @property
    def redirect_domain(self):
        """Gets the redirect_domain of this RedirectConfigForCreateRulesInput.  # noqa: E501


        :return: The redirect_domain of this RedirectConfigForCreateRulesInput.  # noqa: E501
        :rtype: str
        """
        return self._redirect_domain

    @redirect_domain.setter
    def redirect_domain(self, redirect_domain):
        """Sets the redirect_domain of this RedirectConfigForCreateRulesInput.


        :param redirect_domain: The redirect_domain of this RedirectConfigForCreateRulesInput.  # noqa: E501
        :type: str
        """
        if (self._configuration.client_side_validation and
                redirect_domain is not None and len(redirect_domain) > 128):
            raise ValueError("Invalid value for `redirect_domain`, length must be less than or equal to `128`")  # noqa: E501
        if (self._configuration.client_side_validation and
                redirect_domain is not None and len(redirect_domain) < 1):
            raise ValueError("Invalid value for `redirect_domain`, length must be greater than or equal to `1`")  # noqa: E501

        self._redirect_domain = redirect_domain

    @property
    def redirect_http_code(self):
        """Gets the redirect_http_code of this RedirectConfigForCreateRulesInput.  # noqa: E501


        :return: The redirect_http_code of this RedirectConfigForCreateRulesInput.  # noqa: E501
        :rtype: str
        """
        return self._redirect_http_code

    @redirect_http_code.setter
    def redirect_http_code(self, redirect_http_code):
        """Sets the redirect_http_code of this RedirectConfigForCreateRulesInput.


        :param redirect_http_code: The redirect_http_code of this RedirectConfigForCreateRulesInput.  # noqa: E501
        :type: str
        """

        self._redirect_http_code = redirect_http_code

    @property
    def redirect_port(self):
        """Gets the redirect_port of this RedirectConfigForCreateRulesInput.  # noqa: E501


        :return: The redirect_port of this RedirectConfigForCreateRulesInput.  # noqa: E501
        :rtype: str
        """
        return self._redirect_port

    @redirect_port.setter
    def redirect_port(self, redirect_port):
        """Sets the redirect_port of this RedirectConfigForCreateRulesInput.


        :param redirect_port: The redirect_port of this RedirectConfigForCreateRulesInput.  # noqa: E501
        :type: str
        """

        self._redirect_port = redirect_port

    @property
    def redirect_protocol(self):
        """Gets the redirect_protocol of this RedirectConfigForCreateRulesInput.  # noqa: E501


        :return: The redirect_protocol of this RedirectConfigForCreateRulesInput.  # noqa: E501
        :rtype: str
        """
        return self._redirect_protocol

    @redirect_protocol.setter
    def redirect_protocol(self, redirect_protocol):
        """Sets the redirect_protocol of this RedirectConfigForCreateRulesInput.


        :param redirect_protocol: The redirect_protocol of this RedirectConfigForCreateRulesInput.  # noqa: E501
        :type: str
        """

        self._redirect_protocol = redirect_protocol

    @property
    def redirect_uri(self):
        """Gets the redirect_uri of this RedirectConfigForCreateRulesInput.  # noqa: E501


        :return: The redirect_uri of this RedirectConfigForCreateRulesInput.  # noqa: E501
        :rtype: str
        """
        return self._redirect_uri

    @redirect_uri.setter
    def redirect_uri(self, redirect_uri):
        """Sets the redirect_uri of this RedirectConfigForCreateRulesInput.


        :param redirect_uri: The redirect_uri of this RedirectConfigForCreateRulesInput.  # noqa: E501
        :type: str
        """
        if (self._configuration.client_side_validation and
                redirect_uri is not None and len(redirect_uri) > 128):
            raise ValueError("Invalid value for `redirect_uri`, length must be less than or equal to `128`")  # noqa: E501
        if (self._configuration.client_side_validation and
                redirect_uri is not None and len(redirect_uri) < 1):
            raise ValueError("Invalid value for `redirect_uri`, length must be greater than or equal to `1`")  # noqa: E501

        self._redirect_uri = redirect_uri

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
        if issubclass(RedirectConfigForCreateRulesInput, dict):
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
        if not isinstance(other, RedirectConfigForCreateRulesInput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, RedirectConfigForCreateRulesInput):
            return True

        return self.to_dict() != other.to_dict()
