# coding: utf-8

"""
    cdn

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class CertInfoForAddCdnDomainInput(object):
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
        'cert_id': 'str',
        'cert_name': 'str',
        'certificate': 'CertificateForAddCdnDomainInput',
        'desc': 'str',
        'effective_time': 'int',
        'encry_type': 'str',
        'expire_time': 'int',
        'source': 'str'
    }

    attribute_map = {
        'cert_id': 'CertId',
        'cert_name': 'CertName',
        'certificate': 'Certificate',
        'desc': 'Desc',
        'effective_time': 'EffectiveTime',
        'encry_type': 'EncryType',
        'expire_time': 'ExpireTime',
        'source': 'Source'
    }

    def __init__(self, cert_id=None, cert_name=None, certificate=None, desc=None, effective_time=None, encry_type=None, expire_time=None, source=None, _configuration=None):  # noqa: E501
        """CertInfoForAddCdnDomainInput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._cert_id = None
        self._cert_name = None
        self._certificate = None
        self._desc = None
        self._effective_time = None
        self._encry_type = None
        self._expire_time = None
        self._source = None
        self.discriminator = None

        if cert_id is not None:
            self.cert_id = cert_id
        if cert_name is not None:
            self.cert_name = cert_name
        if certificate is not None:
            self.certificate = certificate
        if desc is not None:
            self.desc = desc
        if effective_time is not None:
            self.effective_time = effective_time
        if encry_type is not None:
            self.encry_type = encry_type
        if expire_time is not None:
            self.expire_time = expire_time
        if source is not None:
            self.source = source

    @property
    def cert_id(self):
        """Gets the cert_id of this CertInfoForAddCdnDomainInput.  # noqa: E501


        :return: The cert_id of this CertInfoForAddCdnDomainInput.  # noqa: E501
        :rtype: str
        """
        return self._cert_id

    @cert_id.setter
    def cert_id(self, cert_id):
        """Sets the cert_id of this CertInfoForAddCdnDomainInput.


        :param cert_id: The cert_id of this CertInfoForAddCdnDomainInput.  # noqa: E501
        :type: str
        """

        self._cert_id = cert_id

    @property
    def cert_name(self):
        """Gets the cert_name of this CertInfoForAddCdnDomainInput.  # noqa: E501


        :return: The cert_name of this CertInfoForAddCdnDomainInput.  # noqa: E501
        :rtype: str
        """
        return self._cert_name

    @cert_name.setter
    def cert_name(self, cert_name):
        """Sets the cert_name of this CertInfoForAddCdnDomainInput.


        :param cert_name: The cert_name of this CertInfoForAddCdnDomainInput.  # noqa: E501
        :type: str
        """

        self._cert_name = cert_name

    @property
    def certificate(self):
        """Gets the certificate of this CertInfoForAddCdnDomainInput.  # noqa: E501


        :return: The certificate of this CertInfoForAddCdnDomainInput.  # noqa: E501
        :rtype: CertificateForAddCdnDomainInput
        """
        return self._certificate

    @certificate.setter
    def certificate(self, certificate):
        """Sets the certificate of this CertInfoForAddCdnDomainInput.


        :param certificate: The certificate of this CertInfoForAddCdnDomainInput.  # noqa: E501
        :type: CertificateForAddCdnDomainInput
        """

        self._certificate = certificate

    @property
    def desc(self):
        """Gets the desc of this CertInfoForAddCdnDomainInput.  # noqa: E501


        :return: The desc of this CertInfoForAddCdnDomainInput.  # noqa: E501
        :rtype: str
        """
        return self._desc

    @desc.setter
    def desc(self, desc):
        """Sets the desc of this CertInfoForAddCdnDomainInput.


        :param desc: The desc of this CertInfoForAddCdnDomainInput.  # noqa: E501
        :type: str
        """

        self._desc = desc

    @property
    def effective_time(self):
        """Gets the effective_time of this CertInfoForAddCdnDomainInput.  # noqa: E501


        :return: The effective_time of this CertInfoForAddCdnDomainInput.  # noqa: E501
        :rtype: int
        """
        return self._effective_time

    @effective_time.setter
    def effective_time(self, effective_time):
        """Sets the effective_time of this CertInfoForAddCdnDomainInput.


        :param effective_time: The effective_time of this CertInfoForAddCdnDomainInput.  # noqa: E501
        :type: int
        """

        self._effective_time = effective_time

    @property
    def encry_type(self):
        """Gets the encry_type of this CertInfoForAddCdnDomainInput.  # noqa: E501


        :return: The encry_type of this CertInfoForAddCdnDomainInput.  # noqa: E501
        :rtype: str
        """
        return self._encry_type

    @encry_type.setter
    def encry_type(self, encry_type):
        """Sets the encry_type of this CertInfoForAddCdnDomainInput.


        :param encry_type: The encry_type of this CertInfoForAddCdnDomainInput.  # noqa: E501
        :type: str
        """

        self._encry_type = encry_type

    @property
    def expire_time(self):
        """Gets the expire_time of this CertInfoForAddCdnDomainInput.  # noqa: E501


        :return: The expire_time of this CertInfoForAddCdnDomainInput.  # noqa: E501
        :rtype: int
        """
        return self._expire_time

    @expire_time.setter
    def expire_time(self, expire_time):
        """Sets the expire_time of this CertInfoForAddCdnDomainInput.


        :param expire_time: The expire_time of this CertInfoForAddCdnDomainInput.  # noqa: E501
        :type: int
        """

        self._expire_time = expire_time

    @property
    def source(self):
        """Gets the source of this CertInfoForAddCdnDomainInput.  # noqa: E501


        :return: The source of this CertInfoForAddCdnDomainInput.  # noqa: E501
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source):
        """Sets the source of this CertInfoForAddCdnDomainInput.


        :param source: The source of this CertInfoForAddCdnDomainInput.  # noqa: E501
        :type: str
        """

        self._source = source

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
        if issubclass(CertInfoForAddCdnDomainInput, dict):
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
        if not isinstance(other, CertInfoForAddCdnDomainInput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CertInfoForAddCdnDomainInput):
            return True

        return self.to_dict() != other.to_dict()
