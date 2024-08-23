# coding: utf-8

"""
    iam

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class CreateOAuthProviderRequest(object):
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
        'authorize_template': 'str',
        'authorize_url': 'str',
        'client_id': 'str',
        'client_secret': 'str',
        'description': 'str',
        'identity_map_type': 'int',
        'idp_identity_key': 'str',
        'o_auth_provider_name': 'str',
        'sso_type': 'int',
        'scope': 'str',
        'status': 'int',
        'token_url': 'str',
        'user_info_url': 'str'
    }

    attribute_map = {
        'authorize_template': 'AuthorizeTemplate',
        'authorize_url': 'AuthorizeURL',
        'client_id': 'ClientId',
        'client_secret': 'ClientSecret',
        'description': 'Description',
        'identity_map_type': 'IdentityMapType',
        'idp_identity_key': 'IdpIdentityKey',
        'o_auth_provider_name': 'OAuthProviderName',
        'sso_type': 'SSOType',
        'scope': 'Scope',
        'status': 'Status',
        'token_url': 'TokenURL',
        'user_info_url': 'UserInfoURL'
    }

    def __init__(self, authorize_template=None, authorize_url=None, client_id=None, client_secret=None, description=None, identity_map_type=None, idp_identity_key=None, o_auth_provider_name=None, sso_type=None, scope=None, status=None, token_url=None, user_info_url=None, _configuration=None):  # noqa: E501
        """CreateOAuthProviderRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._authorize_template = None
        self._authorize_url = None
        self._client_id = None
        self._client_secret = None
        self._description = None
        self._identity_map_type = None
        self._idp_identity_key = None
        self._o_auth_provider_name = None
        self._sso_type = None
        self._scope = None
        self._status = None
        self._token_url = None
        self._user_info_url = None
        self.discriminator = None

        self.authorize_template = authorize_template
        self.authorize_url = authorize_url
        self.client_id = client_id
        self.client_secret = client_secret
        if description is not None:
            self.description = description
        self.identity_map_type = identity_map_type
        self.idp_identity_key = idp_identity_key
        self.o_auth_provider_name = o_auth_provider_name
        self.sso_type = sso_type
        if scope is not None:
            self.scope = scope
        if status is not None:
            self.status = status
        self.token_url = token_url
        self.user_info_url = user_info_url

    @property
    def authorize_template(self):
        """Gets the authorize_template of this CreateOAuthProviderRequest.  # noqa: E501


        :return: The authorize_template of this CreateOAuthProviderRequest.  # noqa: E501
        :rtype: str
        """
        return self._authorize_template

    @authorize_template.setter
    def authorize_template(self, authorize_template):
        """Sets the authorize_template of this CreateOAuthProviderRequest.


        :param authorize_template: The authorize_template of this CreateOAuthProviderRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and authorize_template is None:
            raise ValueError("Invalid value for `authorize_template`, must not be `None`")  # noqa: E501

        self._authorize_template = authorize_template

    @property
    def authorize_url(self):
        """Gets the authorize_url of this CreateOAuthProviderRequest.  # noqa: E501


        :return: The authorize_url of this CreateOAuthProviderRequest.  # noqa: E501
        :rtype: str
        """
        return self._authorize_url

    @authorize_url.setter
    def authorize_url(self, authorize_url):
        """Sets the authorize_url of this CreateOAuthProviderRequest.


        :param authorize_url: The authorize_url of this CreateOAuthProviderRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and authorize_url is None:
            raise ValueError("Invalid value for `authorize_url`, must not be `None`")  # noqa: E501

        self._authorize_url = authorize_url

    @property
    def client_id(self):
        """Gets the client_id of this CreateOAuthProviderRequest.  # noqa: E501


        :return: The client_id of this CreateOAuthProviderRequest.  # noqa: E501
        :rtype: str
        """
        return self._client_id

    @client_id.setter
    def client_id(self, client_id):
        """Sets the client_id of this CreateOAuthProviderRequest.


        :param client_id: The client_id of this CreateOAuthProviderRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and client_id is None:
            raise ValueError("Invalid value for `client_id`, must not be `None`")  # noqa: E501

        self._client_id = client_id

    @property
    def client_secret(self):
        """Gets the client_secret of this CreateOAuthProviderRequest.  # noqa: E501


        :return: The client_secret of this CreateOAuthProviderRequest.  # noqa: E501
        :rtype: str
        """
        return self._client_secret

    @client_secret.setter
    def client_secret(self, client_secret):
        """Sets the client_secret of this CreateOAuthProviderRequest.


        :param client_secret: The client_secret of this CreateOAuthProviderRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and client_secret is None:
            raise ValueError("Invalid value for `client_secret`, must not be `None`")  # noqa: E501

        self._client_secret = client_secret

    @property
    def description(self):
        """Gets the description of this CreateOAuthProviderRequest.  # noqa: E501


        :return: The description of this CreateOAuthProviderRequest.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this CreateOAuthProviderRequest.


        :param description: The description of this CreateOAuthProviderRequest.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def identity_map_type(self):
        """Gets the identity_map_type of this CreateOAuthProviderRequest.  # noqa: E501


        :return: The identity_map_type of this CreateOAuthProviderRequest.  # noqa: E501
        :rtype: int
        """
        return self._identity_map_type

    @identity_map_type.setter
    def identity_map_type(self, identity_map_type):
        """Sets the identity_map_type of this CreateOAuthProviderRequest.


        :param identity_map_type: The identity_map_type of this CreateOAuthProviderRequest.  # noqa: E501
        :type: int
        """
        if self._configuration.client_side_validation and identity_map_type is None:
            raise ValueError("Invalid value for `identity_map_type`, must not be `None`")  # noqa: E501

        self._identity_map_type = identity_map_type

    @property
    def idp_identity_key(self):
        """Gets the idp_identity_key of this CreateOAuthProviderRequest.  # noqa: E501


        :return: The idp_identity_key of this CreateOAuthProviderRequest.  # noqa: E501
        :rtype: str
        """
        return self._idp_identity_key

    @idp_identity_key.setter
    def idp_identity_key(self, idp_identity_key):
        """Sets the idp_identity_key of this CreateOAuthProviderRequest.


        :param idp_identity_key: The idp_identity_key of this CreateOAuthProviderRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and idp_identity_key is None:
            raise ValueError("Invalid value for `idp_identity_key`, must not be `None`")  # noqa: E501

        self._idp_identity_key = idp_identity_key

    @property
    def o_auth_provider_name(self):
        """Gets the o_auth_provider_name of this CreateOAuthProviderRequest.  # noqa: E501


        :return: The o_auth_provider_name of this CreateOAuthProviderRequest.  # noqa: E501
        :rtype: str
        """
        return self._o_auth_provider_name

    @o_auth_provider_name.setter
    def o_auth_provider_name(self, o_auth_provider_name):
        """Sets the o_auth_provider_name of this CreateOAuthProviderRequest.


        :param o_auth_provider_name: The o_auth_provider_name of this CreateOAuthProviderRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and o_auth_provider_name is None:
            raise ValueError("Invalid value for `o_auth_provider_name`, must not be `None`")  # noqa: E501

        self._o_auth_provider_name = o_auth_provider_name

    @property
    def sso_type(self):
        """Gets the sso_type of this CreateOAuthProviderRequest.  # noqa: E501


        :return: The sso_type of this CreateOAuthProviderRequest.  # noqa: E501
        :rtype: int
        """
        return self._sso_type

    @sso_type.setter
    def sso_type(self, sso_type):
        """Sets the sso_type of this CreateOAuthProviderRequest.


        :param sso_type: The sso_type of this CreateOAuthProviderRequest.  # noqa: E501
        :type: int
        """
        if self._configuration.client_side_validation and sso_type is None:
            raise ValueError("Invalid value for `sso_type`, must not be `None`")  # noqa: E501

        self._sso_type = sso_type

    @property
    def scope(self):
        """Gets the scope of this CreateOAuthProviderRequest.  # noqa: E501


        :return: The scope of this CreateOAuthProviderRequest.  # noqa: E501
        :rtype: str
        """
        return self._scope

    @scope.setter
    def scope(self, scope):
        """Sets the scope of this CreateOAuthProviderRequest.


        :param scope: The scope of this CreateOAuthProviderRequest.  # noqa: E501
        :type: str
        """

        self._scope = scope

    @property
    def status(self):
        """Gets the status of this CreateOAuthProviderRequest.  # noqa: E501


        :return: The status of this CreateOAuthProviderRequest.  # noqa: E501
        :rtype: int
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this CreateOAuthProviderRequest.


        :param status: The status of this CreateOAuthProviderRequest.  # noqa: E501
        :type: int
        """

        self._status = status

    @property
    def token_url(self):
        """Gets the token_url of this CreateOAuthProviderRequest.  # noqa: E501


        :return: The token_url of this CreateOAuthProviderRequest.  # noqa: E501
        :rtype: str
        """
        return self._token_url

    @token_url.setter
    def token_url(self, token_url):
        """Sets the token_url of this CreateOAuthProviderRequest.


        :param token_url: The token_url of this CreateOAuthProviderRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and token_url is None:
            raise ValueError("Invalid value for `token_url`, must not be `None`")  # noqa: E501

        self._token_url = token_url

    @property
    def user_info_url(self):
        """Gets the user_info_url of this CreateOAuthProviderRequest.  # noqa: E501


        :return: The user_info_url of this CreateOAuthProviderRequest.  # noqa: E501
        :rtype: str
        """
        return self._user_info_url

    @user_info_url.setter
    def user_info_url(self, user_info_url):
        """Sets the user_info_url of this CreateOAuthProviderRequest.


        :param user_info_url: The user_info_url of this CreateOAuthProviderRequest.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and user_info_url is None:
            raise ValueError("Invalid value for `user_info_url`, must not be `None`")  # noqa: E501

        self._user_info_url = user_info_url

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
        if issubclass(CreateOAuthProviderRequest, dict):
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
        if not isinstance(other, CreateOAuthProviderRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateOAuthProviderRequest):
            return True

        return self.to_dict() != other.to_dict()
