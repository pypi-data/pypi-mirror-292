# coding: utf-8

"""
    mcdn

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class ExtraForListCloudAccountsOutput(object):
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
        'access_token': 'str',
        'akamai_endpoint': 'str',
        'gcp_type': 'str',
        'product_id': 'str',
        'refresh_token': 'str',
        'tenant_id': 'str',
        'wangsu_ak_sk_enabled': 'bool'
    }

    attribute_map = {
        'access_token': 'AccessToken',
        'akamai_endpoint': 'AkamaiEndpoint',
        'gcp_type': 'GcpType',
        'product_id': 'ProductId',
        'refresh_token': 'RefreshToken',
        'tenant_id': 'TenantId',
        'wangsu_ak_sk_enabled': 'WangsuAkSkEnabled'
    }

    def __init__(self, access_token=None, akamai_endpoint=None, gcp_type=None, product_id=None, refresh_token=None, tenant_id=None, wangsu_ak_sk_enabled=None, _configuration=None):  # noqa: E501
        """ExtraForListCloudAccountsOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._access_token = None
        self._akamai_endpoint = None
        self._gcp_type = None
        self._product_id = None
        self._refresh_token = None
        self._tenant_id = None
        self._wangsu_ak_sk_enabled = None
        self.discriminator = None

        if access_token is not None:
            self.access_token = access_token
        if akamai_endpoint is not None:
            self.akamai_endpoint = akamai_endpoint
        if gcp_type is not None:
            self.gcp_type = gcp_type
        if product_id is not None:
            self.product_id = product_id
        if refresh_token is not None:
            self.refresh_token = refresh_token
        if tenant_id is not None:
            self.tenant_id = tenant_id
        if wangsu_ak_sk_enabled is not None:
            self.wangsu_ak_sk_enabled = wangsu_ak_sk_enabled

    @property
    def access_token(self):
        """Gets the access_token of this ExtraForListCloudAccountsOutput.  # noqa: E501


        :return: The access_token of this ExtraForListCloudAccountsOutput.  # noqa: E501
        :rtype: str
        """
        return self._access_token

    @access_token.setter
    def access_token(self, access_token):
        """Sets the access_token of this ExtraForListCloudAccountsOutput.


        :param access_token: The access_token of this ExtraForListCloudAccountsOutput.  # noqa: E501
        :type: str
        """

        self._access_token = access_token

    @property
    def akamai_endpoint(self):
        """Gets the akamai_endpoint of this ExtraForListCloudAccountsOutput.  # noqa: E501


        :return: The akamai_endpoint of this ExtraForListCloudAccountsOutput.  # noqa: E501
        :rtype: str
        """
        return self._akamai_endpoint

    @akamai_endpoint.setter
    def akamai_endpoint(self, akamai_endpoint):
        """Sets the akamai_endpoint of this ExtraForListCloudAccountsOutput.


        :param akamai_endpoint: The akamai_endpoint of this ExtraForListCloudAccountsOutput.  # noqa: E501
        :type: str
        """

        self._akamai_endpoint = akamai_endpoint

    @property
    def gcp_type(self):
        """Gets the gcp_type of this ExtraForListCloudAccountsOutput.  # noqa: E501


        :return: The gcp_type of this ExtraForListCloudAccountsOutput.  # noqa: E501
        :rtype: str
        """
        return self._gcp_type

    @gcp_type.setter
    def gcp_type(self, gcp_type):
        """Sets the gcp_type of this ExtraForListCloudAccountsOutput.


        :param gcp_type: The gcp_type of this ExtraForListCloudAccountsOutput.  # noqa: E501
        :type: str
        """

        self._gcp_type = gcp_type

    @property
    def product_id(self):
        """Gets the product_id of this ExtraForListCloudAccountsOutput.  # noqa: E501


        :return: The product_id of this ExtraForListCloudAccountsOutput.  # noqa: E501
        :rtype: str
        """
        return self._product_id

    @product_id.setter
    def product_id(self, product_id):
        """Sets the product_id of this ExtraForListCloudAccountsOutput.


        :param product_id: The product_id of this ExtraForListCloudAccountsOutput.  # noqa: E501
        :type: str
        """

        self._product_id = product_id

    @property
    def refresh_token(self):
        """Gets the refresh_token of this ExtraForListCloudAccountsOutput.  # noqa: E501


        :return: The refresh_token of this ExtraForListCloudAccountsOutput.  # noqa: E501
        :rtype: str
        """
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, refresh_token):
        """Sets the refresh_token of this ExtraForListCloudAccountsOutput.


        :param refresh_token: The refresh_token of this ExtraForListCloudAccountsOutput.  # noqa: E501
        :type: str
        """

        self._refresh_token = refresh_token

    @property
    def tenant_id(self):
        """Gets the tenant_id of this ExtraForListCloudAccountsOutput.  # noqa: E501


        :return: The tenant_id of this ExtraForListCloudAccountsOutput.  # noqa: E501
        :rtype: str
        """
        return self._tenant_id

    @tenant_id.setter
    def tenant_id(self, tenant_id):
        """Sets the tenant_id of this ExtraForListCloudAccountsOutput.


        :param tenant_id: The tenant_id of this ExtraForListCloudAccountsOutput.  # noqa: E501
        :type: str
        """

        self._tenant_id = tenant_id

    @property
    def wangsu_ak_sk_enabled(self):
        """Gets the wangsu_ak_sk_enabled of this ExtraForListCloudAccountsOutput.  # noqa: E501


        :return: The wangsu_ak_sk_enabled of this ExtraForListCloudAccountsOutput.  # noqa: E501
        :rtype: bool
        """
        return self._wangsu_ak_sk_enabled

    @wangsu_ak_sk_enabled.setter
    def wangsu_ak_sk_enabled(self, wangsu_ak_sk_enabled):
        """Sets the wangsu_ak_sk_enabled of this ExtraForListCloudAccountsOutput.


        :param wangsu_ak_sk_enabled: The wangsu_ak_sk_enabled of this ExtraForListCloudAccountsOutput.  # noqa: E501
        :type: bool
        """

        self._wangsu_ak_sk_enabled = wangsu_ak_sk_enabled

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
        if issubclass(ExtraForListCloudAccountsOutput, dict):
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
        if not isinstance(other, ExtraForListCloudAccountsOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ExtraForListCloudAccountsOutput):
            return True

        return self.to_dict() != other.to_dict()
